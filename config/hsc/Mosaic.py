import os
root.colorterms.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsc', 'colorterms.py'))

root.fittingOrder = 9
root.fluxFitOrder = 7
root.fluxFitAbsolute = True
root.internalFitting = True
root.commonFluxCorr = False
root.fluxFitSolveCcd = True

root.astrom.load(os.path.join(os.environ["OBS_SUBARU_DIR"], "config", "hsc", "filterMap.py"))
