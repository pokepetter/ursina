from pandaeditor import *

class SaveSceneButton():

    def __init__(self):
        self.ask_for_scene_name_menu = load_prefab('ask_for_scene_name_menu')
        self.ask_for_scene_name_menu.enabled = False


    def input(self, key):
        if self.entity.hovered and key == 'left mouse down' or key == 'control-s':
            if scene.entity.name == 'untitled_scene':
                self.ask_for_scene_name_menu.enabled = True
                self.ask_for_scene_name_menu.input_field.editing = True
            else:
                save_prefab(scene.entity, 'scenes')
                scene.has_changes = False
                print('saved scene:', 'scenes', scene_entity.name)
