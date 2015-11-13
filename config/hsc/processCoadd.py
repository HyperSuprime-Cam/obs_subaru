"""
HSC-specific overrides for ProcessCoaddTask
(applied after Subaru overrides in ../processCoadd.py).
"""

root.detection.background.useApprox = False
root.detection.background.binSize = 4096
root.detection.background.undersampleStyle = 'REDUCE_INTERP_ORDER'

import os
root.astrometry.solver.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "hsc", "filterMap.py"))
