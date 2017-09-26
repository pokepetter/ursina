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
        self.name_label.is_editor = True
        self.name_label.parent = self
        self.name_label.x = 0
        self.name_label.origin = (.5, .5)
        self.name_label.scale_y = .025
        self.name_label.text = 'selected name'
        self.name_label.text_entity.origin = (-.5,0)
        self.name_label.text_entity.x = -.45
        self.name_label.color = color.gray

        self.transform_labels = list()
        for j in range(3):
            self.vec3_group = Entity()
            self.vec3_group.parent = self
            for i in range(3):
                self.button = load_prefab('editor_button')
                self.button.is_editor = True
                self.button.parent = self.vec3_group
                self.button.origin = (.5, .5)
                self.button.position = (-(i / 3), -.025 - (j * .025))
                self.button.scale = (1 / 3, .025)
                self.button.color = color.gray
                self.button.text = str(i)
                self.button.text_entity.origin = (-.5,0)
                self.transform_labels.append(self.button)

        self.scripts_label = load_prefab('editor_button')
        self.scripts_label.is_editor = True
        self.scripts_label.parent = self
        # self.scripts_label.origin = (.5, .5)
        # self.scripts_label.position = (0, -.025 * 4)
        self.scripts_label.scale_y = .025
        self.scripts_label.color = color.gray
        self.scripts_label.text = 'scripts:'
        self.scripts_label.text_entity.origin = (-.5,0)
        self.scripts_label.text_entity.x = -.45


        self.layout_group = self.add_script('grid_layout')
        self.layout_group.max_x = 1
        self.layout_group.origin = (.5, .5)
        self.layout_group.update_grid()


    def update(self, dt):
        self.t += 1
        if self.t > 100:
            # print('t')
            self.update_inspector()
            self.t = 0
        # if len(scene.editor.selection) > 0:
        #     self.visible = True
        # else:
        #     self.visible = False

    def update_inspector(self):
        if len(scene.editor.selection) == 0:
            return
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

        for i in range(len(self.selected.scripts)):
            self.button = load_prefab('editor_button')
            self.button.is_editor = True
            self.button.parent = self
            self.button.origin = (.5, .5)
            self.button.position = (0, -.025 - 1 - (i * .025))
            self.button.scale = (1, .025)
            self.button.color = color.gray
            self.button.text = str(i)
            self.button.text_entity.origin = (-.5,0)



    #
    # def on_enable(self):
    #     print('enable')
    #     self.visible = True
    #
    # def on_disable(self):
    #     self.visible = False
