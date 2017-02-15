import os
from lsst.utils import getPackageDir

# Reference catalogs
useLsstFormat = True  # Use LSST format catalogs?
if useLsstFormat:
    from lsst.meas.algorithms import LoadIndexedReferenceObjectsTask
    config.loadAstrom.retarget(LoadIndexedReferenceObjectsTask)
    config.loadAstrom.ref_dataset_name = "ps1_pv3_3pi_20170110"
else:
    from lsst.pipe.tasks.setConfigFromEups import setPhotocalConfigFromEups, setAstrometryConfigFromEups
    setPhotocalConfigFromEups(config)
    menu = {"ps1*": {}, # Defaults are fine
           "sdss*": {"astrom.filterMap": {"y": "z"}}, # No y-band, use z instead
           "2mass*": {"astrom.filterMap": {ff: "J" for ff in "grizy"}}, # No optical bands, use J instead
           }
    setAstrometryConfigFromEups(config, menu)

config.loadAstrom.load(os.path.join(getPackageDir("obs_subaru"), "config", "filterMap.py"))
