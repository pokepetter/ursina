import sys
sys.path.append('..')
from pandaeditor import *


class ProjectBrowser(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'project_browser'

        window.size = (1920 * .5, 1080 * .5)

        self.list = Entity()
        self.list.parent = scene.ui
        self.list.scale *= .9
        self.list.model = 'quad'
        self.list.color = color.gray
        self.list.add_script('scrollable')

        for i in range(10):
            self.b = load_prefab('editor_button')
            self.b.is_editor = False
            self.b.collider = 'box'
            self.b.parent = self.list
            self.b.origin = (0, .5)
            self.b.y = .5 - (i * .205)
            self.b.scale = (1, .2)
            self.b.text = 'new project'
            self.b.text_entity.scale *= 3
            self.b.text_entity.align = 'left'
            self.b.text_entity.x = -.45

        # e = Entity()
        # e.model = 'quad'


        # from project_paths import paths
        paths = ['test0, test1, test2']
        for p in paths:
            print('path:', p)
