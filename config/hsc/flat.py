import os
root.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsc', 'isr.py'))
root.isr.doFringe=False

from lsst.obs.hsc.detrends import HscFlatCombineTask
root.combination.retarget(HscFlatCombineTask)
root.combination.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsc', 'vignette.py'))
