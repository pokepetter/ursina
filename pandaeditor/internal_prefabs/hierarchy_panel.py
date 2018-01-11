import sys
sys.path.append("..")
from pandaeditor import *
import os
import uuid
from collections import defaultdict
from itertools import chain
import time

class HierarchyPanel(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'hierarchy_panel'
        self.parent = scene.ui
        self.is_editor = True
        # self.model = 'quad'
        # self.color = color.panda_button
        self.size = 1
        print('scene:', scene)
        self.origin = (-.5, .5)
        self.position = window.top_left
        self.scale = (.249, 1)
        self.editor_collider = 'box'

        self.button_parent = Entity()
        self.button_parent.parent = self
        self.button_parent.y = -.025 * self.size
        self.button_parent.z = -1
        self.max_vertical = 1000
        self.button_size = (1, .025 * self.size)

        self.bg = Entity()
        self.bg.model = 'quad'
        self.bg.color = color.panda_button
        self.bg.parent = self
        self.bg.origin = (-.5, .5)

        self.temp_hierarchy_panel = list()
        self.buttons = list()
        self.bg.add_script('scrollable')
        self.bg.scrollable.target = self.button_parent
        self.t = 0
        self.i = 0

        self.populate()


    def populate(self):

        self.i = 0
        for child in self.button_parent.children:
            destroy(child)
        self.buttons.clear()

        print('-------pop----------')
        for e in scene.entity.children:
            self.traverse_tree(e)

        self.bg.y = (- (self.i + 1) * (self.button_size[1] + .001)) + .001


    def create_button(self, entity, name):
        button = EditorButton()
        button.is_editor = True
        button.parent = self.button_parent
        button.origin = (-.5, .5)
        button.position = (
            0,
            (-self.i * (self.button_size[1] + .001)))
        button.scale = self.button_size * scene.editor_size
        button.color = color.panda_button
        button.text = name[0:min(32, len(name))]
        # button.text = name
        button.text_entity.align = 'left'
        button.text_entity.x = -.5
        # button.text_entity.wordwrap = button.model.getScale(scene.render)[0] * 4

        selection_button = button.add_script('selection_button')
        selection_button.selection_target = entity
        self.buttons.append(button)

        self.i += 1

        return button


    def traverse_tree(self, e, indent=''):
        indent += '  '
        self.create_button(e, indent + e.name)
        for c in e.children:
            self.traverse_tree(c, indent)

        # print(self.buttons)


    def input(self, key):
        if key == 'left mouse down' and self.hovered:
            scene.editor.selection.clear()
            for b in self.buttons:
                b.color = color.panda_button
