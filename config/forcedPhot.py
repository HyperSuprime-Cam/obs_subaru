"""
Subaru-specific overrides for ForcedPhotTask.
"""
from hsc.pipe.tasks.forcedPhot import SubaruReferencesTask
root.references.retarget(SubaruReferencesTask)

# Measurement
root.measurement.algorithms["flux.gaussian"].shiftmax = 10.0

# Enable model mags
try:
    import lsst.meas.extensions.multiShapelet
    root.measurement.algorithms.names |= lsst.meas.extensions.multiShapelet.algorithms
    root.measurement.slots.modelFlux = "multishapelet.combo.flux"
except ImportError:
    print "meas_extensions_multiShapelet is not setup; disabling model mags"
