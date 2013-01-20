"""
Subaru-specific overrides for ForcedPhotTask.
"""
from hsc.pipe.tasks.forcedPhot import SubaruReferencesTask
root.references.retarget(SubaruReferencesTask)

# Measurement
root.measurement.algorithms["flux.gaussian"].shiftmax = 10.0

# Add another aperture flux - it shouldn't be this painful to do (see LSST #2465)
from lsst.meas.algorithms.algorithmRegistry import AlgorithmRegistry, SincFluxConfig
AlgorithmRegistry.register("flux.sinc2", target=SincFluxConfig.Control, ConfigClass=SincFluxConfig)
root.measurement.algorithms["flux.sinc2"].radius = 5.0
root.measurement.algorithms.names |= ["flux.sinc2"]

# Set centroid from the reference source.
root.measurement.algorithms.names |= ["centroid.record"]
root.measurement.slots.centroid = "centroid.record"

# Copy deblending flags
root.copyColumns["deblend.nchild"] = "deblend.nchild"
root.copyColumns["parent"] = "parentObjectId"

# Enable model mags
try:
    import lsst.meas.extensions.multiShapelet
    root.measurement.algorithms.names |= lsst.meas.extensions.multiShapelet.algorithms
    root.measurement.slots.modelFlux = "multishapelet.combo.flux"
except ImportError:
    print "meas_extensions_multiShapelet is not setup; disabling model mags"

