"""Set color terms for HSC"""

from lsst.meas.photocal.colorterms import ColortermConfig, ColortermGroupConfig

root.library = {
    "hsc*": ColortermGroupConfig.fromValues(
        {'g': ColortermConfig.fromValues("g", "g"),
         'r': ColortermConfig.fromValues("r", "r"),
         'i': ColortermConfig.fromValues("i", "i"),
         'z': ColortermConfig.fromValues("z", "z"),
         'y': ColortermConfig.fromValues("y", "y"),
         }),
    "sdss*": ColortermGroupConfig.fromValues(
        {'g': ColortermConfig.fromValues("g", "r", -0.00816446, -0.08366937, -0.00726883),
         'r': ColortermConfig.fromValues("r", "i",  0.00231810,  0.01284177, -0.03068248),
         'i': ColortermConfig.fromValues("i", "z",  0.00130204, -0.16922042, -0.01374245),
         'z': ColortermConfig.fromValues("z", "i", -0.00680620,  0.01353969,  0.01479369),
         'y': ColortermConfig.fromValues("z", "i",  0.01739708,  0.35652971,  0.00574408),
         }),
    "ps1*": ColortermGroupConfig.fromValues(
        {'g': ColortermConfig.fromValues("g", "r",  0.00730066,  0.06508481, -0.01510570),
         'r': ColortermConfig.fromValues("r", "i",  0.00279757,  0.02093734, -0.01877566),
         'i': ColortermConfig.fromValues("i", "z",  0.00166891, -0.13944659, -0.03034094),
         'z': ColortermConfig.fromValues("z", "y", -0.00907517, -0.28840221, -0.00316369),
         'y': ColortermConfig.fromValues("y", "z", -0.00156858,  0.14747401,  0.02880125),
         }),
}
