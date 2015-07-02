import os
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'apertures.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'kron.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'cmodel.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsm.py'))

root.measurement.slots.instFlux = None

root.measurement.algorithms.names += ["countInputs"]
root.measurement.algorithms["flags.pixel"].any = ["CLIPPED"]

root.astrometry.solver.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "filterMap.py"))
root.deblend.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "deblend.py"))
