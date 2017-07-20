import sys
sys.path.append("..")
from pandaeditor import *
# import prefabs

class Editor():
    panel = load_prefab('panel')
    panel.color = color.red
    panel.position = (0, 0, 0)
    panel.scale = (1,1,1)
    panel.texture = 'textures/sketch_2.png'

    toolbar = load_prefab('panel')
    toolbar.origin = (0,0,0)
    toolbar.position = (0, 0, 0.0)
    toolbar.scale = (0.5, 1, 0.5)
    toolbar.color = color.gray
