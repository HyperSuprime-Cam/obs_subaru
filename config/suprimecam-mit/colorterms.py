"""Set color terms for Suprime-Cam with MITLL detectors"""

from lsst.meas.photocal.colorterms import ColortermConfig, ColortermGroupConfig

# From the last page of http://www.naoj.org/staff/nakata/suprime/illustration/colorterm_report_ver3.pdf
# Transformation for griz band between SDSS and SC (estimated with GS83 SEDs)
root.library = {
    "sdss-*": ColortermGroupConfig.fromValues(
        {'g': ColortermConfig.fromValues("g", "r", -0.00569, -0.0427),
         'r': ColortermConfig.fromValues("r", "g", 0.00261, 0.0304),
         'i': ColortermConfig.fromValues("i", "r", 0.00586, 0.0827, -0.0118),
         'z': ColortermConfig.fromValues("z", "i", 0.000329, 0.0608, 0.0219),
     }),
}
