import os
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'apertures.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'kron.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'cmodel.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsm.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'classifiers.py'))

root.measurement.algorithms["flags.pixel"].any.append("CLIPPED")
#
# This isn't good!  There appears to be no way to configure the flags.pixel measurement
# algorithm based on a configuration parameter; see HSC-1342 for a discussion.  The name
# BRIGHT_MASK must match assembleCoaddConfig.brightObjectMaskName
#
root.measurement.algorithms["flags.pixel"].center.append("BRIGHT_MASK")
root.measurement.algorithms["flags.pixel"].any.append("BRIGHT_MASK")

root.measurement.algorithms.names |= ["countInputs"]

root.astrometry.solver.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "filterMap.py"))

root.deblend.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "deblend.py"))
