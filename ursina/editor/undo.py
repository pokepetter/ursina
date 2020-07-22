from copy import deepcopy
from ursina import *


class Undo(Entity):
    def __init__(self):
        super().__init__()
        # self.otoblop = otoblop
        self.undo_cache = list()
        self.undo_index = 0
        # an undo state contains layer_imgs, layer.visible, layer positions


    def input(self, key):

        if held_keys['control']:
            print(self.undo_index)
            if key == 'z' and self.undo_index > 0:
                self.undo_index -= 1
                # self.undo_index = clamp(self.undo_index, 0, len(self.undo_cache)-1)
                self.undo()

            if key == 'y' and self.undo_index < len(self.undo_cache):
                print('redo')
                self.redo()
                self.undo_index += 1
                # self.undo_index = clamp(self.undo_index, 0, len(self.undo_cache)-1)


    def record_undo(self, func):
        self.undo_cache.append(func)
        self.undo_index += 1


    def undo(self):
        # self.undo_cache[self.undo_index]()
        action, a, b = self.undo_cache[self.undo_index]
        print('undid:', action, b, a)
        action(b, a)
        print(self.undo_cache, self.undo_index)


    def redo(self):
        action, a, b = self.undo_cache[self.undo_index]
        action(a, b)



sys.modules['undo'] = Undo()
