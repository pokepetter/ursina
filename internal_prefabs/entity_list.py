import sys
sys.path.append("..")
from pandaeditor import *
import os
import uuid
from collections import defaultdict
import time

class EntityList(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'entity_list'
        self.parent = scene.ui

        self.color = color.black33
        self.t = 0
        self.buttons = list()

        self.max_vertical = 100
        self.button_size = (.08, .01)

        self.origin = (-.5, .5)
        self.position = (-.5, .2)
        # self.scale = (.5, .5)

        self.temp_entity_list = list()
        # self.scripts.append(self)



    def display(self, id, nodes, level):
        print('%s%s%s' % ('  ' * level, '\\__', id))
        for child in sorted(nodes.get(id, [])):
            self.display(child, nodes, level + 1)




    def populate(self):
        # return
        start_time = time.time()
        for b in self.buttons:
            destroy(b)
        self.buttons.clear()

        # self.temp_entity_list = list(scene.entities)
        # for e in reversed(self.temp_entity_list):
        #     if e.is_editor:
        #         self.temp_entity_list.remove(e)
        #
        # self.temp_entity_list.sort()
        #
        # hierarchy_list = list(self.temp_entity_list)
        # parentless = list(self.temp_entity_list)
        # indents = [0] * len(self.temp_entity_list)
        #
        # for e in self.temp_entity_list:
        #     for orphan in parentless:
        #         if orphan.parent == e:
        self.temp_entity_list = list(scene.entities)
        for e in reversed(self.temp_entity_list):
            if e.is_editor:
                self.temp_entity_list.remove(e)

        page_ids = []
        for e in self.temp_entity_list:
            page_ids.append((
                e.this,
                e.parent.this
                ))
        # page_ids = [
        #     (22, 4), (45, 1), (1, 1), (4, 4),
        #     (566, 45), (7, 7), (783, 566), (66, 1), (300, 8),
        #     (8, 4), (101, 7), (80, 22), (17, 17), (911, 66)
        # ]
        # for e in page_ids:
        #     print('id:', e)
        print(page_ids)

        nodes, roots = defaultdict(set), set()

        for article, parent in page_ids:
            if article == parent:
                roots.add(article)
            else:
                nodes[parent].add(article)

        # print('nodes', nodes)
        # nodes now looks something like this:
        # {1: [45, 66], 66: [911], 4: [22, 8], 22: [80],
        #  7: [101], 8: [300], 45: [566], 566: [783]}

        for id in sorted(roots):
            self.display(id, nodes, 0)


        y = 0
        x = 0
        for e in self.temp_entity_list:
            if not e.is_editor:
                button = load_prefab('editor_button')
                button.is_editor = True
                button.parent = self
                button.origin = (-.5, .5)
                button.position = (
                    x * (self.button_size[0]),
                    (-y * (self.button_size[1])))
                button.scale = self.button_size
                button.color = color.panda_button
                button.text = e.name
                # button.text_entity.size = .5
                selection_button = button.add_script('selection_button')
                selection_button.selection_target = e
                self.buttons.append(button)

                y += 1
                if y >= self.max_vertical:
                    y = 0
                    x += 1




        print("--- %s seconds ---" % (time.time() - start_time))
    # if __name__ == '__main__':
    #     populate()
