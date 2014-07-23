root.measurement.algorithms.names |= ["flux.aperture"]
# Roughly (1.0, 1.4, 2.0, 2.8, 4.0, 5.7, 8.0, 11.3, 16.0, 22.6 arcsec) in diameter: 2**(0.5*i)
# (assumes 0.168 arcsec pixels on coadd)
root.measurement.algorithms["flux.aperture"].radii = [3.0, 4.5, 6.0, 9.0, 12.0, 17.0, 25.0, 35.0, 50.0, 70.0]

# Use a large aperture to be independent of seeing in calibration
root.calibrate.measurement.algorithms["flux.sinc"].radius = 12.0

# Use a large aperture to be independent of seeing in calibration
root.measurement.algorithms["flux.sinc"].radius = 12.0

root.measurement.slots.instFlux = None

try:
    import lsst.meas.extensions.photometryKron
    root.measurement.algorithms.names |= ["flux.kron"]
except ImportError:
    print "Unable to import lsst.meas.extensions.photometryKron: Kron fluxes disabled"

# Enable CModel mags (unsetup meas_multifit or use $MEAS_MULTIFIT_DIR/config/disable.py to disable)
import os
try:
    root.load(os.path.join(os.environ['MEAS_MULTIFIT_DIR'], 'config', 'enable.py'))
except KeyError, ImportError:
    print "Cannot import lsst.meas.multifit: disabling CModel measurements"

# Enable HSM Regaussianization shear measurement (unsetup meas_extensions_shapeHSM to disable)
try:
    import lsst.meas.extensions.shapeHSM
    root.measurement.algorithms.names |= ["shape.hsm.regauss"]
except ImportError:
    print "Cannot import lsst.meas.extensions.shapeHSM: disabling shear measurement"
