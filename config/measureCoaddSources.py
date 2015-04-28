import os
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'apertures.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'kron.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'cmodel.py'))
root.measurement.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsm.py'))

root.deblend.maxNumberOfPeaks = 20

root.measurement.algorithms["flags.pixel"].any = ["CLIPPED"]

root.astrometry.solver.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "filterMap.py"))
