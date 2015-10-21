# Load from sub-configurations
import os
for sub in ("makeCoaddTempExp", "backgroundReference", "assembleCoadd", "detectCoaddSources"):
    path = os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "hsc", sub + ".py")
    if os.path.exists(path):
        getattr(root, sub).load(path)
