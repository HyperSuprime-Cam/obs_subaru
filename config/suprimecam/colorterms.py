"""Set color terms for Suprime-Cam with Hamamatsu detectors"""

from lsst.meas.photocal.colorterms import ColortermConfig, ColortermGroupConfig

root.library = {
    "sdss-*": ColortermGroupConfig.fromValues(
        {'g': ColortermConfig.fromValues("g", "r", -0.00928, -0.0824),
         'r': ColortermConfig.fromValues("r", "i", -0.00282, -0.0498, -0.0149),
         'i': ColortermConfig.fromValues("i", "z", 0.00186, -0.140, -0.0196),
         'z': ColortermConfig.fromValues("z", "i", -4.03e-4, 0.0967, 0.0210),
         'B': ColortermConfig.fromValues("g", "r",  0.02461907,  0.20098328, 0.00858468),
         'V': ColortermConfig.fromValues("g", "r", -0.03117934, -0.63134136, 0.05056544),
         'R': ColortermConfig.fromValues("r", "i", -0.01179613, -0.25403307, 0.00696479),
         'I': ColortermConfig.fromValues("i", "r",  0.01078282,  0.26727768, 0.00747123),
     }),
}
