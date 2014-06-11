# Add another aperture flux - it shouldn't be this painful to do (see LSST #2465)
if False: # This doesn't pickle
    from lsst.meas.algorithms.algorithmRegistry import AlgorithmRegistry, SincFluxConfig
    AlgorithmRegistry.register("flux.sinc2", target=SincFluxConfig.Control, ConfigClass=SincFluxConfig)
    root.measurement.algorithms["flux.sinc2"].radius = 5.0
    root.measurement.algorithms.names |= ["flux.sinc2"]

# Enable model mags, disable Gaussian mags (which aren't really forced)
root.measurement.algorithms.names -= ["flux.gaussian"]
root.measurement.slots.instFlux = None

# Enable CModel mags (unsetup meas_multifit or use $MEAS_MULTIFIT_DIR/config/disable.py to disable)
import os
try:
    root.load(os.path.join(os.environ['MEAS_MULTIFIT_DIR'], 'config', 'enable.py'))
except KeyError, ImportError:
    print "Cannot import lsst.meas.multifit: disabling CModel measurements"
