import os
from ursina import *
import psutil
from hurry.filesize import size


class MemoryCounter(Text):
    def __init__(self, **kwargs):
        super().__init__()
        self.parent = camera.ui
        self.position = window.bottom_right
        self.origin = (0.5, -0.5)

        self.process = psutil.Process(os.getpid())
        self.i = 0

        for key, value in kwargs.items():
            setattr(self, key, value)

    def update(self):
        self.i += 1
        if self.i > 10:
            self.text = 'mem:' + str(size(self.process.memory_info().rss))

            self.i = 0


if __name__ == '__main__':
    app = Ursina()
    MemoryCounter()
    '''
    Displays the amount of memory used in the bottom right corner
    '''
    app.run()
