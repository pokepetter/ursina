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
        self.origin = (.5, .5)
        self.position = (.5, .45)
        self.scale = (.15, .9)

        # append self so update() runs
        self.scripts.append(self)

        self.name_label = load_prefab('editor_button')
        self.name_label.parent = self
        self.name_label.x = 0
        self.name_label.origin = (.5, .5)
        self.name_label.scale_y = .025
        self.name_label.text = 'selected name'
        self.name_label.text_entity.origin = (-.5,0)
        self.name_label.text_entity.x = -.45

        self.transform_labels = list()
        for j in range(3):
            self.vec3_group = Entity()
            self.vec3_group.parent = self
            for i in range(3):
                self.button = load_prefab('editor_button')
                self.button.parent = self.vec3_group
                self.button.origin = (.5, .5)
                self.button.position = (-(i / 3), 0)
                self.button.scale = (1 / 3.05, .025)
                self.button.text = str(i)
                self.button.text_entity.origin = (-.5,0)
                self.transform_labels.append(self.button)

        self.scripts_label = load_prefab('editor_button')
        self.scripts_label.parent = self
        self.scripts_label.scale_y = .025
        self.scripts_label.text = 'scripts:'
        self.scripts_label.text_entity.origin = (-.5,0)
        self.scripts_label.text_entity.x = -.45

        # self.scripts_layout_group = self.add_script('grid_layout')
        # self.scripts_layout_group.max_x = 1
        # self.scripts_layout_group.spacing = [0, .001]
        # self.scripts_layout_group.origin = (.5, .5)
        # self.scripts_layout_group.update_grid()

        self.add_script_button = load_prefab('editor_button')
        self.add_script_button.parent = self
        self.add_script_button.scale_y = .025
        self.add_script_button.text = 'add script'
        self.add_script_button.text_entity.origin = (-.5,0)
        self.add_script_button.text_entity.x = -.45


        self.layout_group = self.add_script('grid_layout')
        self.layout_group.max_x = 1
        self.layout_group.spacing = [0, .001]
        self.layout_group.origin = (.5, .5)
        self.layout_group.update_grid()

        self.script_labels = list()

        self.t = 0


        #testing
        cube = Entity()
        cube.name = 'cube'
        cube.model = 'cube'
        cube.color = color.red
        cube.add_script('grid_layout')
        cube.add_script('test')
        self.selected = cube
        for i in range(8*8):
            c = Entity()
            c.parent = cube
            c.y = random.randrange(0, 2)
            c.name = 'cube'
            c.model = 'cube'
            c.color = color.red

        cube.grid_layout.update_grid()
        cube.rotation_x = 90


    def update(self, dt):
        self.t += 1
        if self.t > 50:
            # print('updating inspector')
            self.update_inspector()
            self.t = 0
        # if len(scene.editor.selection) > 0:
        #     self.visible = True
        # else:
        #     self.visible = False

    def update_inspector(self):
        # if len(scene.editor.selection) == 0:
        #     return
        # self.selected = scene.editor.selection[0]
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


    # def draw_scripts(self):
        # for b in self.script_buttons:


        # for s in self.selected.scripts:
        #     self.button = load_prefab('editor_button')
        #     self.button.parent = self.scripts_label
        #     self.button.name = 'x'
        #
        #
        #     if visible_script.contains(s.__class__):
        #         for attr in s:
        for e in self.scripts_label.children:
            destroy(e)

        for i in range(len(self.selected.scripts)):
            # print('script:', self.selected.scripts[i].__class__.__name__)
            self.button = load_prefab('editor_button')
            self.button.parent = self.scripts_label
            self.button.origin = (.5, .5)
            self.button.position = (.1, - i - 1)
            self.button.scale = (1, 1)
            self.button.color = color.red
            self.button.text = self.selected.scripts[i].__class__.__name__
            self.button.text_entity.origin = (-.5,0)
            self.button.text_entity.x = -.5


        self.add_script_button.y = -.5


    #
    # def on_enable(self):
    #     print('enable')
    #     self.visible = True
    #
    # def on_disable(self):
    #     self.visible = False
