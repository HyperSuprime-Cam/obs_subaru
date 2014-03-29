"""Set color terms for HSC"""

from lsst.meas.photocal.colorterms import Colorterm
import lsst.obs.hsc.colorterms
Colorterm.setColorterms(lsst.obs.hsc.colorterms.colortermsData)
lsst.obs.hsc.colorterms.setFromAstrometryNetData(verbose=True)
