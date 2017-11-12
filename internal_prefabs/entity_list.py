import sys
sys.path.append("..")
from pandaeditor import *
import os
import uuid
from collections import defaultdict
from itertools import chain
import time

class EntityList(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'entity_list'
        self.parent = scene.ui
        self.is_editor = True
        self.model = 'quad'
        self.color = color.panda_button
        self.origin = (-.5, .5)
        self.position = window.top_left
        self.scale = (.199, 1)
        self.editor_collider = 'box'

        self.button_parent = Entity()
        self.button_parent.parent = self
        self.button_parent.y = -.025
        self.button_parent.z = -1
        self.max_vertical = 1000
        self.button_size = (1, .015)

        self.temp_entity_list = list()
        self.buttons = list()
        self.add_script('scrollable')
        self.scrollable.target = self.button_parent
        # print('t:', self.scrollable.target)
        self.scripts.append(self)
        self.t = 0
        self.i = 0

        self.populate()
    # def update(self, dt):
    #     self.t += 1
    #     if self.t > 1000:
    #         self.populate()
    #         self.t = 0


    def populate(self):

        self.i = 0
        for child in self.button_parent.children:
            destroy(child)
        self.buttons.clear()

        print('------------------')
        for e in scene.entity.children:
            self.traverse_tree(e)


    def create_button(self, entity, name):
        button = load_prefab('editor_button')
        # button.is_editor = True
        button.parent = self.button_parent
        button.origin = (-.5, .5)
        button.position = (
            0,
            (-self.i * (self.button_size[1] + .001)))
        button.scale = self.button_size
        button.color = color.panda_button
        button.text = name
        button.text_entity.align = 'left'
        button.text_entity.x = -.5

        selection_button = button.add_script('selection_button')
        selection_button.selection_target = entity
        self.buttons.append(button)
        # print(button)

        self.i += 1

        return button


    def traverse_tree(self, e, indent=''):
        indent += '-'
        self.create_button(e, indent + e.name)
        for c in e.children:
            self.traverse_tree(c, indent)

        print(self.buttons)


        # print("--- %s seconds ---" % (time.time() - start_time))
    # if __name__ == '__main__':
    #     populate()
    # def __iter__(self):
    #     # "implement the iterator protocol"
    #     for v in chain(*map(iter, self.children)):
    #         yield v
    #     yield self.value
