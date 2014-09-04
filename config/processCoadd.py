import os
root.calibrate.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'apertures.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'apertures.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'kron.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'cmodel.py'))

root.measurement.slots.instFlux = None

# Enable HSM Regaussianization shear measurement (unsetup meas_extensions_shapeHSM to disable)
try:
    import lsst.meas.extensions.shapeHSM
    root.measurement.algorithms.names |= ["shape.hsm.regauss"]
except ImportError:
    print "Cannot import lsst.meas.extensions.shapeHSM: disabling shear measurement"
