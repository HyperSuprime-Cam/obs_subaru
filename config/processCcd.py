"""
Subaru-specific overrides for ProcessCcdTask (applied before SuprimeCam- and HSC-specific overrides).
"""

# This was a horrible choice of defaults: only the scaling of the flats
# should determine the relative normalisations of the CCDs!
root.isr.assembleCcd.doRenorm = False

# Cosmic rays and background estimation
root.calibrate.repair.cosmicray.nCrPixelMax = 1000000
root.calibrate.repair.cosmicray.cond3_fac2 = 0.4
root.calibrate.background.binSize = 256
root.calibrate.background.undersampleStyle = 'REDUCE_INTERP_ORDER'
root.calibrate.detection.background.binSize = 256
root.calibrate.detection.background.undersampleStyle='REDUCE_INTERP_ORDER'
root.detection.background.binSize = 256
root.detection.background.undersampleStyle = 'REDUCE_INTERP_ORDER'

# PSF determination
root.calibrate.measurePsf.starSelector.name = "objectSize"
root.calibrate.measurePsf.starSelector["objectSize"].sourceFluxField = "initial.flux.psf"
try:
    import lsst.meas.extensions.psfex.psfexPsfDeterminer
    root.calibrate.measurePsf.psfDeterminer["psfex"].spatialOrder = 2
    root.calibrate.measurePsf.psfDeterminer.name = "psfex"
except ImportError as e:
    print "WARNING: Unable to use psfex: %s" % e
    root.calibrate.measurePsf.psfDeterminer.name = "pca"

# Astrometry
try:
    # the next line will fail if hscAstrom is not setup; in that case we just use lsst.meas.astrm
    from lsst.obs.subaru.astrometry import SubaruAstrometryTask
    root.calibrate.astrometry.retarget(SubaruAstrometryTask)
    root.calibrate.astrometry.solver.filterMap = { 'B': 'g',
                                                   'V': 'r',
                                                   'R': 'r',
                                                   'I': 'i',
                                                   'y': 'z',
                                                   }
except ImportError:
    print "hscAstrom is not setup; using LSST's meas_astrom instead"

# Reference catalog may not have as good star/galaxy discrimination as our data
root.calibrate.photocal.badFlags += ["classification.extendedness",]

# Detection
root.detection.isotropicGrow = True
root.detection.returnOriginalFootprints = False

# Measurement
root.doWriteSourceMatches = True
root.measurement.algorithms.names |= ["jacobian", "focalplane"]

root.measurement.algorithms.names |= ["flux.aperture"]
# Roughly (1.0, 1.4, 2.0, 2.8, 4.0, 5.7, 8.0, 11.3, 16.0, 22.6 arcsec) in diameter: 2**(0.5*i)
root.measurement.algorithms["flux.aperture"].radii = [3.0, 4.5, 6.0, 9.0, 12.0, 17.0, 25.0, 35.0, 50.0, 70.0]

# Use a large aperture to be independent of seeing in calibration
root.calibrate.measurement.algorithms["flux.sinc"].radius = 12.0
root.measurement.algorithms["flux.sinc"].radius = 12.0

try:
    import lsst.meas.extensions.photometryKron
    root.measurement.algorithms.names |= ["flux.kron"]
    # If we want to apply aperture corrections to the kron fluxes, we need to measure them in calibrate
    root.calibrate.measurement.algorithms.names |= ["flux.kron"]
except ImportError:
    print "Cannot import lsst.meas.extensions.photometryKron: disabling Kron measurements"

root.measurement.algorithms['classification.extendedness'].fluxRatio = 0.95

# Enable deblender for processCcd
root.measurement.doReplaceWithNoise = True
root.doDeblend = True
root.deblend.maxNumberOfPeaks = 20
