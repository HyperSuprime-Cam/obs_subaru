import os
root.load(os.path.join(os.environ['OBS_SUBARU_DIR'], 'config', 'hsc', 'isr.py'))
root.isr.doDefect=False
root.isr.doBrighterFatter = False
