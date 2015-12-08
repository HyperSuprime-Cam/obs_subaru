import os

root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'apertures.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'kron.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'cmodel.py'))

# Disable Gaussian mags (which aren't really forced)
root.measurement.algorithms.names -= ["flux.gaussian"]
root.measurement.slots.instFlux = None

root.measurement.algorithms.names |= ["countInputs", "variance"]
root.measurement.algorithms["flags.pixel"].any.append("CLIPPED")

root.measurement.algorithms["flags.pixel"].center.append("BRIGHT_OBJECT")
root.measurement.algorithms["flags.pixel"].any.append("BRIGHT_OBJECT")
