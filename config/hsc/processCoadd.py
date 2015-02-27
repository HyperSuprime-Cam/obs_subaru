"""
HSC-specific overrides for ProcessCoaddTask
(applied after Subaru overrides in ../processCoadd.py).
"""

try:
    detection = root.detectCoaddSources.detection
except:
    detection = root.detection

detection.background.useApprox = False
detection.background.binSize = 4096
detection.background.undersampleStyle = 'REDUCE_INTERP_ORDER'

