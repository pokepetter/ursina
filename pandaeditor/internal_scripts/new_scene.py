import sys
sys.path.append("..")
from pandaeditor import *

class NewScene():

    def __init__(self):
        self.is_editor = True
        self.target = None

        self.waiting_for_reply = False
        # self.submit_name = scene.editor.save_scene_button.save_scene_button.ask_for_scene_name_menu.save_button


    def input(self, key):
        if key == 'left mouse down' and self.entity.hovered:
            # self.target.enabled = not self.target.enabled
            if scene.has_changes:
                # ask for save / discard

                self.waiting_for_reply = True

            # ask for scene name

            destroy(scene.entity)
            scene.entity = Entity()
            scene.entity.name = 'untitled_scene'
            scene.editor.entity_list_header.text = scene.entity.name

            # save_prefab

    def update(self, dt):
        if self.waiting_for_reply:
            pass
