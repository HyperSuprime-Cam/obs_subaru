#!/usr/bin/env python

# NOTE: THIS MODULE SHOULD NOT BE IMPORTED BY __init__.py, AS IT IMPORTS THE OPTIONAL hscAstrom PACKAGE.

import numpy
import lsst.pex.config as pexConfig
import lsst.daf.base as dafBase
import lsst.pipe.base as pipeBase
import lsst.meas.astrom as measAstrom
import lsst.pipe.tasks.astrometry as ptAstrometry
import hsc.meas.astrom as hscAstrom

class SubaruAstrometryConfig(ptAstrometry.AstrometryConfig):
    solver = pexConfig.ConfigField(
        dtype=hscAstrom.TaburAstrometryConfig,
        doc = "Configuration for the Tabur astrometry solver"
        )
    failover = pexConfig.Field(dtype=bool, doc="Fail over from hscAstrom to meas_astrom?", default=False)

    allowFailedAstrometry = pexConfig.Field(dtype=bool, doc="Proceed even if astrometry fails?", default=False)

# Use hsc.meas.astrom, failing over to lsst.meas.astrom
class SubaruAstrometryTask(ptAstrometry.AstrometryTask):
    ConfigClass = SubaruAstrometryConfig
    AstrometerClass = hscAstrom.TaburAstrometry

    @pipeBase.timeMethod
    def astrometry(self, exposure, sources, bbox=None):
        """Solve astrometry to produce WCS

        @param exposure Exposure to process
        @param sources Sources
        @param bbox Bounding box
        @return Star matches, match metadata
        """
        assert exposure, "No exposure provided"

        self.log.log(self.log.INFO, "Solving astrometry")

        wcs = exposure.getWcs()
        if wcs is None:
            self.log.warn("Unable to use hsc.meas.astrom; reverting to lsst.meas.astrom")
            return ptAstrometry.AstrometryTask.astrometry(exposure, sources, bbox=bbox)

        astrom = None
        try:
            astrom = self.astrometer.determineWcs(sources, exposure)
            if astrom is None:
                raise RuntimeError("hsc.meas.astrom failed to determine the WCS")
        except Exception, e:
            self.log.warn("hsc.meas.astrom failed (%s)" % e)
            if self.config.failover:
                self.log.info("Failing over to lsst.meas.astrom....")
                astrometer = measAstrom.Astrometry(self.config.solver, log=self.log)
                astrom = astrometer.determineWcs(sources, exposure)

        if astrom is None and self.config.allowFailedAstrometry:
            matches = []
            matchMeta = dafBase.PropertySet()
        else:
            if astrom is None:
                raise RuntimeError("Unable to solve astrometry for %s" % exposure.getDetector().getId())

            wcs = astrom.getWcs()
            matches = astrom.getMatches()
            matchMeta = astrom.getMatchMetadata()
            if matches is None or len(matches) == 0:
                raise RuntimeError("No astrometric matches for %s" % exposure.getDetector().getId())
            self.log.info("%d astrometric matches for %s" % (len(matches), exposure.getDetector().getId()))
            exposure.setWcs(wcs)

        # Apply WCS to sources
        for source in sources:
            distorted = source.get(self.centroidKey)
            sky = wcs.pixelToSky(distorted.getX(), distorted.getY())
            source.setCoord(sky)

        self.display('astrometry', exposure=exposure, sources=sources, matches=matches)

        metadata = exposure.getMetadata()
        for key in self.metadata.names():
            val = self.metadata.get(key)
            if isinstance(val, tuple):
                self.log.logdebug("Value of %s is a tuple: %s" % (key, val))
                val = val[-1]

            try:
                if isinstance(val, int) and val > 0x8fffff:
                    metadata.setLong(key, val)
                else:
                    metadata.set(key, val)
            except Exception, e:
                self.log.warn("Value of %s == %s is invalid; %s" % (key, val, e))

        metadata.set('NOBJ_BRIGHT', len(sources))
        metadata.set('NOBJ_MATCHED', len(matches))
        metadata.set('WCS_NOBJ', len(matches))

        return pipeBase.Struct(matches=matches, matchMeta=matchMeta)

    def refitWcs(self, exposure, sources, matches):
        sip = super(SubaruAstrometryTask, self).refitWcs(exposure, sources, matches)
        order = self.config.solver.sipOrder if self.config.solver.calculateSip else 0

        if sip:
            rms = sip.getScatterOnSky().asArcseconds()
        else:
            wcs = exposure.getWcs()
            ref = numpy.array([wcs.skyToPixel(m.first.getCoord()) for m in matches])
            src = numpy.array([m.second.getCentroid() for m in matches])
            diff = ref - src
            rms = diff.std() * wcs.pixelScale().asArcseconds()

        metadata = exposure.getMetadata()
        metadata.set('WCS_SIPORDER', order)
        metadata.set('WCS_RMS', rms)
        return sip
