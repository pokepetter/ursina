import sys
sys.path.append("..")
from pandaeditor import *
import os

class Inspector(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'inspector'
        self.parent = scene.ui
        self.is_editor = True
        self.model = 'quad'
        self.color = color.panda_button
        self.origin = (-.5, .5)
        self.position = window.top_left
        self.x += .2
        self.scale = (.2, 1)

        self.button_height = .025
        self.script_amount = 0

        # append self so update() runs
        self.scripts.append(self)

        self.name_label = load_prefab('editor_button')
        self.name_label.parent = self
        self.name_label.origin = (-.5, .5)
        self.name_label.scale_y = self.button_height
        self.name_label.text = 'selected name'
        self.name_label.text_entity.align = 'left'
        self.name_label.text_entity.x = -.45

        self.transform_labels = list()
        for j in range(3):
            self.vec3_group = Entity()
            self.vec3_group.parent = self
            for i in range(3):
                self.button = load_prefab('editor_button')
                self.button.parent = self.vec3_group
                self.button.origin = (-.5, .5)
                self.button.position = ((i / 3), 0)
                self.button.scale = (1 / 3.05, self.button_height)
                self.button.text = str(i)
                self.button.text_entity.align = 'left'
                self.transform_labels.append(self.button)

        self.model_field = self.create_button('model: ')
        self.color_field = self.create_button('color: ')
        self.texture_field = self.create_button('texture: ')


        self.scripts_label = load_prefab('editor_button')
        self.scripts_label.parent = self
        # self.scripts_label.y = self.button_height * -5
        self.scripts_label.scale_y = self.button_height
        self.scripts_label.text = 'scripts:'
        self.scripts_label.text_entity.align = 'left'
        self.scripts_label.text_entity.x = -.45
        # self.scripts_label.add_script('menu_toggler')

        self.add_script_button = self.create_button('add script')
        self.menu_toggler = self.add_script_button.add_script('menu_toggler')
        self.menu_toggler_1 = self.add_script_button.add_script('menu_toggler')

        self.internal_scripts_browser = load_prefab('filebrowser')
        self.internal_scripts_browser.is_editor = True
        self.internal_scripts_browser.parent = scene.ui
        self.internal_scripts_browser.position = (0, 0)
        self.internal_scripts_browser.enabled = False
        self.internal_scripts_browser.file_types = ('.py')
        self.internal_scripts_browser.path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'internal_scripts')
        self.internal_scripts_browser.button_type = 'add_script_button'
        self.menu_toggler.target = self.internal_scripts_browser

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.is_editor = True
        self.filebrowser.parent = scene.ui
        self.filebrowser.position = (.0, 0)
        self.filebrowser.enabled = False
        self.filebrowser.file_types = ('.py')
        self.filebrowser.path = os.path.join(os.path.dirname(application.asset_folder), 'scripts')
        self.filebrowser.button_type = 'add_script_button'
        self.menu_toggler_1.target = self.filebrowser


        self.layout_group = self.add_script('grid_layout')
        self.layout_group.max_x = 1
        self.layout_group.spacing = [0, .001]
        self.layout_group.origin = (-.5, .5)
        self.layout_group.update_grid()

        self.script_labels = list()

        self.t = 0


    def create_button(self, name=''):
        button = load_prefab('editor_button')
        button.parent = self
        button.scale_y = self.button_height
        button.text = name
        button.text_entity.align = 'left'
        button.text_entity.x = -.45
        return button


    def update(self, dt):
        self.t += 1
        if self.t > 10:
            # print('updating inspector')
            self.update_inspector()
            self.t = 0


    def update_inspector(self):

        if len(scene.editor.selection) == 0:
            self.x = 1.2
            return
        else:
            self.position = (window.top_left[0] + .2, window.top_right[1] - .025)

        self.selected = scene.editor.selection[0]

        self.name_label.text = self.selected.name
        self.transform_labels[0].text = str(int(self.selected.x))
        self.transform_labels[1].text = str(int(self.selected.y))
        self.transform_labels[2].text = str(int(self.selected.z))
        self.transform_labels[3].text = str(int(self.selected.rotation_x))
        self.transform_labels[4].text = str(int(self.selected.rotation_y))
        self.transform_labels[5].text = str(int(self.selected.rotation_z))
        self.transform_labels[6].text = str(int(self.selected.scale_x))
        self.transform_labels[7].text = str(int(self.selected.scale_y))
        self.transform_labels[8].text = str(int(self.selected.scale_z))


        self.model_field.text = 'model: ' + self.selected.model.name
        self.color_field.text = 'color: ' + self.selected.model.color
        self.texture_field.text = 'texture: ' + self.selected.texture.name


        if len(self.selected.scripts) != self.script_amount: # if script changed, update
            self.script_amount = len(self.selected.scripts)

            for e in self.scripts_label.children:
                try:
                    destroy(e)
                except:
                    pass

            for i in range(1, len(self.selected.scripts)):  # skip first one to ignore EditorButton
                # if self.selected.script[i]._class__.__name__ == 'EditorButton':
                #     pass
                print('script:', self.selected.scripts[i].__class__.__name__)
                self.button = load_prefab('editor_button')
                self.button.parent = self.scripts_label
                self.button.origin = (-.5, .5)
                self.button.position = (0, - i - 1)
                self.button.scale = (1, 1)
                self.button.color = color.red
                self.button.text = self.selected.scripts[i].__class__.__name__
                self.button.text_entity.align = 'left'
                self.button.text_entity.x = -.45

                scripts_vars = [item for item in dir(self.selected.scripts[i]) if not item.startswith('_')]
                print('vars:', scripts_vars)

                j = 1
                for var in scripts_vars:
                    if var == 'entity':
                        continue

                    self.var_button = load_prefab('editor_button')
                    self.var_button.parent = self.button
                    self.var_button.origin = (-.5, .5)
                    self.var_button.position = (0, - j)
                    self.var_button.scale = (1, 1)
                    self.var_button.color = color.yellow
                    self.var_button.text = var
                    self.var_button.text_entity.origin = (-.5,0)
                    self.var_button.text_entity.x = -.4

                    varvalue = getattr(self.selected.scripts[i], var)

                    j += 1


                    self.add_script_button.y -= j * -.025
                self.add_script_button.y -= (len(self.selected.scripts) +7) * -.025
