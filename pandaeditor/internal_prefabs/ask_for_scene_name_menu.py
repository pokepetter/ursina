import sys
sys.path.append("..")
from pandaeditor import *

class AskForSceneNameMenu(Entity):

    def __init__(self):
        super().__init__()
        self.parent = scene.ui
        self.model = 'quad'
        self.scale = (.25, .025)

        self.window_title = EditorButton()
        self.window_title.parent = self.model
        self.window_title.color = color.black
        self.window_title.text = 'save scene as...'

        self.window_title.text_entity.align = 'left'
        self.window_title.text_entity.x = -.45
        self.window_title.remove_script('editor_draggable')

        self.input_field = InputField()
        self.input_field.is_editor = True
        self.input_field.parent = self.model
        self.input_field.y = -1

        self.save_button = EditorButton()
        self.save_button.parent = self.model
        self.save_button.text = 'save'
        self.save_button.y = -2

        self.close_button = EditorButton()
        self.close_button.name = 'close_button'
        self.close_button.parent = self
        self.close_button.position = (0, 0, 10)
        self.close_button.scale *= 100
        self.close_button.color = color.black33
        self.close_button.highlight_color = color.black33
        menu_toggler = self.close_button.add_script('menu_toggler')
        menu_toggler.target = self


    def input(self, key):
        if self.save_button.hovered and key == 'left mouse down' or key == 'enter':
            print('save field:', self.input_field.text)
            if self.input_field.text != '':
                scene.entity.name = self.input_field.text
                scene.editor.entity_list_header.text = self.input_field.text
                save_prefab(scene.entity, application.scene_folder)
                self.enabled = False
                print('saved scene:', 'scenes', scene_entity.name)

# class Save():
if __name__ == '__main__':
    app = PandaEditor()
    test = AskForSceneNameMenu()
    app.run()
