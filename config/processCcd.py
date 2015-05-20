"""
Subaru-specific overrides for ProcessCcdTask (applied before SuprimeCam- and HSC-specific overrides).
"""

import os

# This was a horrible choice of defaults: only the scaling of the flats
# should determine the relative normalisations of the CCDs!
root.isr.assembleCcd.doRenorm = False

# Cosmic rays and background estimation
root.calibrate.repair.cosmicray.nCrPixelMax = 1000000
root.calibrate.repair.cosmicray.cond3_fac2 = 0.4
root.calibrate.background.binSize = 128
root.calibrate.background.undersampleStyle = 'REDUCE_INTERP_ORDER'
root.calibrate.detection.background.binSize = 128
root.calibrate.detection.background.undersampleStyle='REDUCE_INTERP_ORDER'
root.detection.background.binSize = 128
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
    root.calibrate.astrometry.solver.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "filterMap.py"))
except ImportError:
    print "hscAstrom is not setup; using LSST's meas_astrom instead"

# Demand astrometry and photoCal succeed
root.calibrate.requireAstrometry = True
root.calibrate.requirePhotoCal = True

# Detection
root.detection.isotropicGrow = True
root.detection.returnOriginalFootprints = False

# Measurement
root.doWriteSourceMatches = True
root.measurement.algorithms.names |= ["jacobian", "focalplane"]

# Activate calibration of measurements: required for aperture corrections
root.calibrate.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'apertures.py'))
root.calibrate.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'cmodel.py'))
root.calibrate.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'kron.py'))
root.calibrate.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsm.py'))
if "shape.hsm.regauss" in root.calibrate.measurement.algorithms:
    root.calibrate.measurement.algorithms["shape.hsm.regauss"].deblendNChild = "" # no deblending has been done

root.calibrate.measureCurveOfGrowth.nAperture = 8 # 35 pixels is sufficient and more stable than 70

# Activate deep measurements
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'apertures.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'kron.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsm.py'))
# Note no CModel: it's slow.

# Enable deblender for processCcd
root.measurement.doReplaceWithNoise = True
root.doDeblend = True
root.deblend.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'deblend.py'))
root.deblend.maskLimits["NO_DATA"] = 0.25 # Ignore sources that are in the vignetted region
