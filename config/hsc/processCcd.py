"""
HSC-specific overrides for ProcessCcdTask
(applied after Subaru overrides in ../processCcd.py).
"""

import os
root.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsc', 'isr.py'))
root.calibrate.photocal.colorterms.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsc',
                                                     'colorterms.py'))

root.calibrate.measurePsf.starSelector.name='objectSize'
root.calibrate.measurePsf.starSelector['objectSize'].widthMin=0.9

root.calibrate.astrometry.solver.sipOrder = 3
root.calibrate.astrometry.solver.catalogMatchDist = 2.0

root.measurement.algorithms["jacobian"].pixelScale = 0.168

# Do not use NO_DATA pixels for fringe subtraction.
root.isr.fringe.stats.badMaskPlanes=['SAT', 'NO_DATA']
