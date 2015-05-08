"""
Subaru-specific overrides for ProcessExposureTask (applied before SuprimeCam- and HSC-specific overrides).
"""

import os
root.processCcd.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "processCcd.py"))

root.curveOfGrowth.nAperture = 8 # 35 pixels is sufficient and more stable than 70
root.curveOfGrowth.fracInterpolatedMax = 0.25
root.curveOfGrowth.skyNoiseFloor = 0.5
