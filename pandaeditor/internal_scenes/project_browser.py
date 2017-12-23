from pandaeditor import *


class ProjectBrowser(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'project_browser'

        window.size = (1920 * .6, 1080 * .6)
        # window.name = self.name
        # window.color = color.color(0, 0, .9)
        # color.text_color = color.color(0, 0, .1)
        # camera.ui.scale *= .95

        self.bg = Entity()
        self.bg.parent = scene.ui
        self.bg.model = 'quad'
        self.bg.scale_x *= camera.aspect_ratio
        self.bg.texture = 'project_browser_bg'
        self.bg.color = color.gray

        # self.title = Text()
        self.title = Text()
        self.title.parent = scene.ui
        self.title.text = 'Choose Project'
        # self.title.align = 'center'
        self.title.scale /= 4
        self.title.position = (-.5 * camera.aspect_ratio + .05, .425)

        self.list = Entity()
        self.list.parent = scene.ui
        self.list.x = -.5 * camera.aspect_ratio + .05
        # self.list.scale *= .9

        # from project_paths import paths
        self.paths = ('new', 'open', 'test0', 'test1', 'test2', 'test3')
        self.index = 0
        if len(self.paths) > 0:
            self.index = 1



        for i in range(len(self.paths)):
            self.b = Button()
            s = self.b.add_script(ProjectBrowserButton())
            s.index = i
            self.b.parent = self.list
            self.b.collider = 'box'
            self.b.origin = (-.5, .5)
            self.b.x = 0 + (i * .34)
            self.b.scale = (.33 * 1, .33)
            self.b.color = color.color(i * 20, .2, 1, .5)
            if i == 0:
                self.b.color = color.color(0, 0, .75, .5)
            # self.b.texture = 'white_cube'

            t = Text()
            t.text = 'Name' + str(i)
            t.parent = self.b.model
            t.scale *= .5
            t.position = (-.5, .57)
            if i == 0:
                t.text = '+'
                t.align = 'center'
                t.scale *= 3
                t.position = (0, 0)

            if i > 0:
                t = Text()
                t.text = self.paths[i]
                t.parent = self.b.model
                t.scale *= .25
                t.position = (-.5, -.55)


    def input(self, key):
        if len(self.paths) > 5:
            if key == 'scroll up':
                self.list.x += .1
            if key == 'scroll down':
                self.list.x -= .1

            self.list.x = clamp(self.list.x, (-len(self.paths) * .34) + .84 , -.84)


class ProjectBrowserButton():

    def input(self, key):
        if self.entity.hovered:
            if (key == 'left mouse down'
            or key == 'space'
            or key == 'enter'
            and self.index > 0):
                self.load_project(scene.entity.paths[self.index])

    def on_mouse_enter(self):
        scene.entity.index = self.index

    def load_project(self, path):
        print('loading project:', path)
        if os.path.isdir(path):
            print('yay')
            subprocess.call('python.exe ' + path + 'main.py')
            # run process python.exe, path + main.py, editor=True
            os._exit(0)     # force exit
        else:
            print('project not found at:', path)

if __name__ == '__main__':
    app = main.PandaEditor()
    load_scene('project_browser')
    # t = ProjectBrowser()
    app.run()
