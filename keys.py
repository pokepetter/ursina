import sys
from collections import defaultdict


class Keys(object):

    def __init__(self):
        self.control = False
        self.left_control = False
        self.right_control = False

        self.shift = False
        self.left_shift = False
        self.right_shift = False

        self.alt = False
        self.left_alt = False
        self.right_alt = False

        self.held_keys = defaultdict(lambda: 0)


    def input(self, key):
        if key.endswith('up'):
            self.held_keys[key[:-3]] = 0
        else:
            self.held_keys[key] = 1

        # if key == 'left control':
        #     self.left_control = True
        #     self.control = True
        # if key == 'right control':
        #     self.right_control = True
        #     self.control = True
        # if key == 'left control up':
        #     self.left_control = False
        #     if not self.right_control:
        #         self.control = False
        # if key == 'right control up':
        #     self.right_control = False
        #     if not self.left_control:
        #         self.control = False
        #
        # if key == 'left shift':
        #     self.left_shift = True
        #     self.shift = True
        # if key == 'right shift':
        #     self.right_shift = True
        #     self.shift = True
        # if key == 'left shift up':
        #     self.left_shift = False
        #     if not self.right_shift:
        #         self.shift = False
        # if key == 'right shift up':
        #     self.right_shift = False
        #     if not self.left_shift:
        #         self.shift = False
        #
        # if key == 'left alt':
        #     self.left_alt = True
        #     self.alt = True
        # if key == 'right alt':
        #     self.right_alt = True
        #     self.alt = True
        # if key == 'left alt up':
        #     self.left_alt = False
        #     if self.right_alt == False:
        #         self.alt = False
        # if key == 'right alt up':
        #     self.right_alt = False
        #     if not self.left_alt:
        #         self.alt = False

sys.modules[__name__] = Keys()
