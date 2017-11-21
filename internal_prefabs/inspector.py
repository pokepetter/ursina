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
        # self.model = 'quad'
        # self.color = color.panda_button
        self.origin = (-.5, .5)
        self.position = window.top_left
        self.x += .25
        self.y = .5
        self.scale = (.25, 1)

        self.button_height = .025 * scene.editor_font_size
        self.script_amount = 0

        # append self so update() runs
        self.scripts.append(self)

# name_label
        self.name_label = self.create_button('name_label')
        self.name_label.color = (color.turquoise + color.black) / 2
        self.name_label.text = 'selected name'

# transform_labels
        self.transform_labels = list()
        for j in range(3):
            self.vec3_group = Entity()
            self.vec3_group.parent = self
            self.vec3_group.scale_y = self.button_height
            for i in range(3):
                self.button = load_prefab('editor_button')
                # self.button = self.create_button('transform_field')
                self.button.parent = self.vec3_group
                self.button.origin = (-.5, .5)
                self.button.position = ((i / 3), 0)
                self.button.scale = (1 / 3.05, 1)
                self.button.text = str(i)
                self.button.text_entity.align = 'left'
                self.button.text_entity.x = -.43
                self.transform_labels.append(self.button)

        # self.space = self.create_button('space')
        self.space = Entity()
        self.space.model = 'quad'
        self.space.parent = self
        self.space.scale_y = .01
        self.space.origin = (-.5, .5)
        self.space.color = color.panda_button

# model_field
        self.model_field = self.create_button('model: ')
        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.parent = camera.ui
        self.filebrowser.position = (0,0)
        self.filebrowser.name = 'replace_model_filebrowser'
        self.filebrowser.file_types = ('.egg')
        self.filebrowser.path = os.path.join(os.path.dirname(application.asset_folder), 'pandaeditor/internal_models')
        self.filebrowser.button_type = 'replace_model_button'
        self.menu_toggler = self.model_field.add_script('menu_toggler')
        self.menu_toggler.target = self.filebrowser

# color_field
        self.color_field = self.create_button('color: ')
        self.color_field_preview = Entity()
        self.color_field_preview.parent = self.color_field.model
        self.color_field_preview.model = 'quad'
        self.color_field_preview.origin = (.5, 0)
        self.color_field_preview.position = (.5, 0)
        self.color_field_preview.scale_x = .33
        self.color_select = load_prefab('panel')
        self.color_select.color = color.panda_button
        self.color_select.parent = camera.ui
        self.color_select.scale *= .5
        self.color_select.enabled = False
        self.menu_toggler = self.color_field.add_script('menu_toggler')
        self.menu_toggler.target = self.color_select

# texture_field
        self.texture_field = self.create_button('texture: ')
        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.parent = camera.ui
        self.filebrowser.position = (0,0)
        self.filebrowser.name = 'replace_texture_filebrowser'
        self.filebrowser.file_types = ('.png', '.jpg')
        self.filebrowser.path = os.path.join(os.path.dirname(application.asset_folder), 'textures')
        self.filebrowser.button_type = 'replace_texture_button'
        self.menu_toggler = self.texture_field.add_script('menu_toggler')
        self.menu_toggler.target = self.filebrowser

        self.scripts_label = self.create_button('editor_button')
        self.scripts_label.parent = self
        self.scripts_label.text = ' '

        self.add_script_button = self.create_button('add script')
        self.add_script_button.text_entity.align = 'center'
        self.add_script_button.text_entity.x = 0
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


        self.new_y = 0

        for i in range(1, len(self.children)):

            self.new_y -= self.children[i-1].scale_y + .001
            self.children[i].y = self.new_y

        self.script_labels = list()

        self.t = 0


    def create_button(self, name='', height=.025*scene.editor_size):
        button = load_prefab('editor_button')
        button.parent = self
        button.origin = (-.5, .5)
        button.scale_y = height
        button.text = name[0:min(32, len(name))]
        button.text_entity.align = 'left'
        button.text_entity.x = -.475
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
        # else:
        self.x = window.top_left[0] + .25

        self.selected = scene.editor.selection[0]
        # print('egjnie:', self.selected)

        name = self.selected.name
        self.name_label.text = name[0:min(32, len(name))]
        self.transform_labels[0].text = str(round(self.selected.x, 2))
        self.transform_labels[1].text = str(round(self.selected.y, 2))
        self.transform_labels[2].text = str(round(self.selected.z, 2))

        self.transform_labels[3].text = str(round(self.selected.rotation_x, 2))
        self.transform_labels[4].text = str(round(self.selected.rotation_y, 2))
        self.transform_labels[5].text = str(round(self.selected.rotation_z, 2))

        self.transform_labels[6].text = str(round(self.selected.scale_x, 2))
        self.transform_labels[7].text = str(round(self.selected.scale_y, 2))
        self.transform_labels[8].text = str(round(self.selected.scale_z, 2))

        if self.selected.model:
            self.model_field.text = ('m ' + self.selected.model.name)

        if self.selected.color:
            self.color_field.text = (
                'color: '
                + str(self.selected.color[0]) + ','
                + str(self.selected.color[1]) + ','
                + str(self.selected.color[2])
                )
            self.color_field_preview.color = self.selected.color

        if self.selected.texture:
            self.texture_field.text = 'texture: ' + self.selected.texture.name

        if len(self.selected.scripts) != self.script_amount: # if script changed, update
            self.script_amount = len(self.selected.scripts)

            for e in self.scripts_label.children:
                try:
                    destroy(e)
                except:
                    pass

            self.prev_script_length = 0
            for i in range(1, len(self.selected.scripts)):  # skip first one to ignore EditorButton
                self.button = self.create_button(self.selected.scripts[i].__class__.__name__)
                self.button.parent = self.scripts_label
                self.button.color = color.red
                self.button.position = (0, - i - 1 - self.prev_script_length)
                self.button.scale = (1, 1)
                scripts_vars = [item for item in dir(self.selected.scripts[i]) if not item.startswith('_')]
                self.prev_script_length = len(scripts_vars) - 1


                j = 1
                for var in scripts_vars:
                    if var == 'entity':
                        continue

                    self.var_button = self.create_button(var)
                    self.var_button.parent = self.button
                    self.var_button.origin = (-.5, .5)
                    self.var_button.position = (0, - j)
                    self.var_button.scale = (1, 1)
                    self.var_button.color = color.orange
                    self.var_button.text = var
                    self.var_button.text_entity.origin = (-.5,0)
                    self.var_button.text_entity.x = -.4

                    varvalue = getattr(self.selected.scripts[i], var)

                    j += 1


                    # self.add_script_button.y -= j * -.025
                # self.add_script_button.y -= (len(self.selected.scripts)+7) * .025
