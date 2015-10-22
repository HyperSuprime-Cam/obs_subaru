"""
HSC-specific overrides for ProcessCoaddTask
(applied after Subaru overrides in ../processCoadd.py).
"""

detection.background.useApprox = False
detection.background.binSize = 4096
detection.background.undersampleStyle = 'REDUCE_INTERP_ORDER'

import os
root.astrometry.solver.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "hsc", "filterMap.py"))
