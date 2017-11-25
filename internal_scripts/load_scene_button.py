import sys
sys.path.append("..")
from pandaeditor import *

class LoadSceneButton():

    def __init__(self):
        self.path = None

    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            if self.path:
                scene_name = os.path.basename(self.path).split('.')[0]
                load_scene(scene_name)
                scene.editor.entity_list.populate()

                for e in scene.entities:
                    try:
                        e.editor_collider = 'box'
                        e.collider.stash()
                    except:
                        print('couldnt add editor collider to:', e)
