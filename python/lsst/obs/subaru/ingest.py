import re
import datetime
import os

from lsst.pipe.tasks.ingest import IngestTask, ParseTask, IngestArgumentParser, RegisterTask, RegistryContext, IngestConfig
from lsst.pex.config import Field, ConfigurableField

try:
    import psycopg2 as pgsql
    havePgSql = True
    db = None
except ImportError:
    try:
        from pg8000 import DBAPI as pgsql
        havePgSql = True
        db = None
    except ImportError:
        havePgSql = False
from lsst.daf.butlerUtils import PgSqlConfig

class HscIngestArgumentParser(IngestArgumentParser):
    def _parseDirectories(self, namespace):
        """Don't do any 'rerun' hacking: we want the raw data to end up in the root directory"""
        namespace.input = namespace.rawInput
        namespace.output = namespace.rawOutput
        namespace.calib = None
        del namespace.rawInput
        del namespace.rawCalib
        del namespace.rawOutput
        del namespace.rawRerun

class HscIngestTask(IngestTask):
    ArgumentParser = HscIngestArgumentParser

class PgsqlRegistryContext(RegistryContext):
    """Context manager to provide a pgsql registry
    """
    def __init__(self, registryName, createTableFunc=None):
        """Construct a context manager

        @param registryName: Name of registry file
        @param createTableFunc: Function to create tables
        """
        self.registryName = registryName
        try:
            pgsqlConf = PgSqlConfig()
            pgsqlConf.load(registryName)
            self.conn = pgsql.connect(host=pgsqlConf.host, port=pgsqlConf.port, 
                                      user=pgsqlConf.user, password=pgsqlConf.password,
                                      database=pgsqlConf.db)
            cur = self.conn.cursor()

            makeTable = True
            cur.execute("SELECT relname FROM pg_class WHERE relkind='r' AND relname='raw'")
            rows = cur.fetchall()
            if len(rows) != 0 and createTableFunc is None:
                makeTable = False

            if makeTable:
                cmd = "DROP TABLE IF EXISTS raw, raw_skyTile, raw_visit"
                cur.execute(cmd)

                createTableFunc(self.conn)

        except Exception, e:
            print e
            sys.exit(1)
        finally:
            del cur
                
    def __exit__(self, excType, excValue, traceback):
        self.conn.commit()
        self.conn.close()
        if excType is None:
            pass
        return False # Don't suppress any exceptions

class PgsqlRegisterTask(RegisterTask):

    def openRegistry(self, butler, create=False, dryrun=False):
        """Open the registry and return the connection handle.

        @param butler  Data butler, from which the registry file is determined
        @param create  Clobber any existing registry and create a new one?
        @param dryrun  Don't do anything permanent?
        @return Database connection
        """
        if dryrun:
            from contextlib import contextmanager
            @contextmanager
            def fakeContext():
                yield
            return fakeContext()
        registryName = os.path.join(butler.mapper.root, "registry_pgsql.py")
        context = PgsqlRegistryContext(registryName, self.createTable if create else None)
        return context

    def createTable(self, conn):
        """Create the registry tables

        One table (typically 'raw') contains information on all files, and the
        other (typically 'raw_visit') contains information on all visits.

        @param conn    Database connection
        """
        cur = conn.cursor()
        cmd = "create table %s (id SERIAL NOT NULL PRIMARY KEY, " % self.config.table
        cmd += ",".join([("%s %s" % (col, PgsqlColType(colType))) for col,colType in self.config.columns.items()])
        if len(self.config.unique) > 0:
            cmd += ", UNIQUE(" + ",".join(self.config.unique) + ")"
        cmd += ")"
        cur.execute(cmd)

        cmd = "create table %s_visit (" % self.config.table
        cmd += ",".join([("%s %s" % (col, PgsqlColType(self.config.columns[col]))) for col in self.config.visit])
        cmd += ", UNIQUE(" + ",".join(set(self.config.visit).intersection(set(self.config.unique))) + ")"
        cmd += ")"
        cur.execute(cmd)
        del cur

        conn.commit()

    def check(self, conn, info):
        """Check for the presence of a row already

        Not sure this is required, given the 'ignore' configuration option.
        """
        if conn == None:
            return False        # For dryrun
        if self.config.ignore or len(self.config.unique) == 0:
            return False # Our entry could already be there, but we don't care
        sql = "SELECT COUNT(*) FROM %s WHERE " % self.config.table
        sql += " AND ".join(["%s=%d" % (col, info[col]) for col in self.config.unique])

        cur = conn.cursor()
        cur.execute(sql)
        if cur.fetchone()[0] > 0:
            del cur
            return True
        del cur
        return False

    def addRow(self, conn, info, dryrun=False, create=False):
        """Add a row to the file table (typically 'raw').

        @param conn    Database connection
        @param info    File properties to add to database
        """
        sql = "INSERT"
        sql += " INTO %s (" % self.config.table
        sql += ", ".join([col for col in self.config.columns])
        sql += ") SELECT "
        sql += ", ".join([PgsqlFormat(colType, info[col]) for col, colType in self.config.columns.items()])
        if self.config.ignore:
            sql += " WHERE NOT EXISTS (SELECT 1 FROM %s WHERE " % self.config.table
            sql += " AND ".join(["%s=%d" % (col, info[col]) for col in self.config.unique])
            sql += ")"
        if dryrun:
            print "Would execute: '%s'" % sql
        else:
            cur = conn.cursor()
            cur.execute(sql)
            del cur

    def addVisits(self, conn, dryrun=False):
        """Generate the visits table (typically 'raw_visits') from the
        file table (typically 'raw').

        @param conn    Database connection
        """
        sql = "INSERT INTO %s_visit SELECT DISTINCT " % self.config.table
        sql += ", ".join(self.config.visit)
        sql += " FROM %s t" % self.config.table
        sql += " WHERE NOT EXISTS (SELECT t2.visit FROM %s_visit t2 WHERE t2.visit = t.visit)" % self.config.table
        if dryrun:
            print "Would execute: %s" % sql
        else:
            cur = conn.cursor()
            cur.execute(sql)
            del cur

def PgsqlColType(colType):

    if colType == 'text':
        return 'VARCHAR(32)'
    elif colType == 'int':
        return 'INT'
    elif colType == 'double':
        return 'FLOAT8'
    else:
        return 'VARCHAR(32)'

def PgsqlFormat(colType, value):

    if colType == 'text':
        return "'%s'" % (value)
    elif colType == 'int':
        return "%d" % (int(value))
    elif colType == 'double':
        return "%f" % (float(value))
    else:
        return "'%s'" % (value)

class PgsqlIngestConfig(IngestConfig):
    """Configuration for PgsqlIngestTask"""
    parse = ConfigurableField(target=ParseTask, doc="File parsing")
    register = ConfigurableField(target=PgsqlRegisterTask, doc="Registry entry")
    allowError = Field(dtype=bool, default=False, doc="Allow error in ingestion?")
    clobber = Field(dtype=bool, default=False, doc="Clobber existing file?")

class HscPgsqlIngestTask(HscIngestTask):
    ConfigClass = PgsqlIngestConfig

def datetime2mjd(date_time):

    YY = date_time.year
    MO = date_time.month
    DD = date_time.day
    HH = date_time.hour
    MI = date_time.minute
    SS = date_time.second

    if MO == 1 or MO == 2:
        mm = MO + 12
        yy = YY - 1
    else:
        mm = MO
        yy = YY

    dd = DD + (HH/24.0 + MI/24.0/60.0 + SS/24.0/3600.0)

    A = int(365.25*yy);
    B = int(yy/400.0);
    C = int(yy/100.0);
    D = int(30.59*(mm-2));

    mjd = A + B -C + D  + dd - 678912;

    return mjd

class HscParseTask(ParseTask):
    DAY0 = 55927  # Zero point for  2012-01-01  51544 -> 2000-01-01

    def translate_field(self, md):
        field = md.get("OBJECT").strip()
        if field == "#":
            field = "UNKNOWN"
        field = re.sub(r'\W', '_', field).upper() # replacing inappropriate characters for file path and upper()

        return field

    def translate_visit(self, md):
        expId = md.get("EXP-ID").strip()
        m = re.search("^HSCE(\d{8})$", expId)  # 2016-06-14 and new scheme
        if m is not None:
            visit = m.groups()[0]
            visit = int(visit)
            return visit

        m = re.search("^HSC([A-Z])(\d{6})00$", expId)
        if not m:
            raise RuntimeError("Unable to interpret EXP-ID: %s" % expId)
        letter, visit = m.groups()
        visit = int(visit)
        if int(visit) == 0:
            # Don't believe it
            frameId = md.get("FRAMEID").strip()
            m = re.search("^HSC([A-Z])(\d{6})\d{2}$", frameId)
            if not m:
                raise RuntimeError("Unable to interpret FRAMEID: %s" % frameId)
            letter, visit = m.groups()
            visit = int(visit)
            if visit % 2: # Odd?
                visit -= 1
        return visit + 1000000*(ord(letter) - ord("A"))

    def getTjd(self, md):
        """Return truncated (modified) Julian Date"""
        return int(md.get('MJD')) - self.DAY0

    def translate_pointing(self, md):
        """This value was originally called 'pointing', and intended to be used
        to identify a logical group of exposures.  It has evolved to simply be
        a form of truncated Modified Julian Date, and is called 'visitID' in
        some versions of the code.  However, we retain the name 'pointing' for
        backward compatibility.
        """
        try:
            return self.getTjd(md)
        except:
            pass

        try:
            dateobs = md.get("DATE-OBS")
            m = re.search(r'(\d{4})-(\d{2})-(\d{2})', dateobs)
            year, month, day = m.groups()
            obsday = datetime.datetime(int(year), int(month), int(day), 0, 0, 0)
            mjd = datetime2mjd(obsday)
            return int(mjd) - day0
        except:
            pass

        self.log.warn("Unable to determine suitable 'pointing' value; using 0")
        return 0

    # CCD index mapping for commissioning run 2
    CCD_MAP_COMMISSIONING_2 = {112: 106,
                               107: 105,
                               113: 107,
                               115: 109,
                               108: 110,
                               114: 108,
                               }
    def translate_ccd(self, md):
        """Focus CCDs were numbered incorrectly in the readout software during
        commissioning run 2.  We need to map to the correct ones.
        """
        ccd = int(md.get("DET-ID"))
        try:
            tjd = self.getTjd(md)
        except:
            return ccd

        if tjd > 390 and tjd < 405:
            ccd = self.CCD_MAP_COMMISSIONING_2.get(ccd, ccd)

        return ccd

    def translate_filter(self, md):
        """Want upper-case filter names"""
        try:
            return md.get('FILTER01').strip().upper()
        except:
            return "Unrecognized"
