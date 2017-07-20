import sys
sys.path.append("..")
from pandaeditor import *
# import prefabs

class Editor():
    panel = load_prefab('panel')
    panel.color = color.lime
    panel.position = (.25, 0, 0)
    panel.scale = (0.5,1,1)
    panel.texture = 'textures/sketch_2.png'
