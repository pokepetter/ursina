import os
import psutil
from hurry.filesize import size


class MemoryCounter(Text):
    def __init__(self):
        super().__init__()
        self.parent = camera.ui
        self.position = window.bottom_right
        self.origin = (.5, -.5)
        self.scale *= .1

        self.process = psutil.Process(os.getpid())
        self.i = 0


    def update(self):
        self.i += 1
        if self.i > 10:
            self.text = 'mem:' + str(size(self.process.memory_info().rss))

            self.i = 0
