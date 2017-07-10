from pandaeditor import *

from os import walk
import os

from ui import UI
import button
from editor_camera import EditorCamera


class MyApp(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        # camera
        # lens = OrthographicLens()
        lens = PerspectiveLens()
        lens.setFov(40)
        lens.setNear(0.1)
        lens.setFar(100)
        # lens.setFocalLength(50)
        aspect_ratio = screen_size[0] / screen_size[1]
        lens.setAspectRatio(aspect_ratio)
        base.cam.node().setLens(lens)

        # input
        base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        self.accept('keystroke', self.input)

        base.disableMouse()
        mouse.parent = self
        mouse.mouse_watcher = base.mouseWatcherNode

        self.accept('mouse1', mouse.input, ['left mouse down'])
        self.accept('mouse3', mouse.input, ['right mouse down'])
        self.accept('mouse2', mouse.input, ['middle mouse down'])

        self.accept('mouse1-up', mouse.input, ['left mouse up'])
        self.accept('mouse3-up', mouse.input, ['right mouse up'])
        self.accept('mouse2-up', mouse.input, ['middle mouse up'])

        #collision
        collision.parent = self

        # f = []
        # self_directory = os.path.dirname(os.path.abspath(__file__))
        # models_path = os.path.join(self_directory, 'models')
        # i = 0
        # for (dirpath, dirnames, filenames) in walk(models_path):
        # files = os.listdir(models_path)
        # for i in range(len(files)):
        #     print(files[i])
            # ornament = ''
            # for j in range(len(files[i]) * 2):
            #     ornament += '-'


        # game objects
        self.things = []
        self.scene = Thing()

        self.editor_camera = Thing()
        self.editor_camera.name = 'editor_camera'
        self.editor_camera.parent = self.render
        # self.editor_camera.add_script(EditorCamera)
        camera.cam = base.camera
        camera.lens = lens
        camera.render = self.render
        # camera.y = -100
        camera.global_position = (0,-100,0)
        camera.rotation = (0,0,0)
        self.things.append(self.editor_camera)

        # UI
        # ui_thing = Thing()
        # ui_thing.name = 'ui'
        # ui_thing.parent = self.render
        # # ui_thing.position = (0, -2, 0)
        # ui_thing.node_path.setPos(Vec3(0,-2,0))
        # ui_thing.model = loader.loadModel('models/quad_rounded.egg')
        # # ui_thing.model.hide()
        # ui_script = ui_thing.add_script(UI)
        # ui_script.fit_to_screen()
        # self.things.append(ui_thing)
        #
        #
        # for i in range(1):
        #     button = Thing()
        #     button.name = 'button'
        #     button.parent = ui_thing
        #     button.model = loader.loadModel('models/quad_rounded.egg')
        #     button.global_position = (.125, 0, 0.0)
        #     button.scale = (0.5, 0.5, 0.5)
        #     button.origin = (-1, 0, 0)
        #     button_script = button.add_script(Button)
        #     button_script.ui = ui_script
        #     button_script.color = color.gray
        #     button_script.set_up()
        #     self.things.append(button)



        thing = Thing()
        thing.name = 'empty'
        thing.parent = self.render
        thing.model = self.loader.loadModel('models/cube.egg')
        thing.model.reparentTo(thing.node_path)
        thing.global_position = (0,0,0)
        # thing.scale = .1
        # thing.collision = True
        # thing.collider
        # thing.add_script('player')
        thing.add_script(EditorCamera)
        self.things.append(thing)
        prev_thing = thing

        thing = Thing()
        thing.name = 'empty'
        thing.parent = prev_thing
        thing.model = self.loader.loadModel('models/cube.egg')
        thing.model.reparentTo(thing.node_path)
        thing.global_position = (0,0,0)



        # create button
        # thing = Thing()
        # thing.name = 'button'
        # thing.origin = (-1,0,-1)
        # thing.position = (0 * aspect_ratio ,0, 0)
        # thing.scale = 0.04
        # thing.size = (500,0,512)
        # # button.collision = True
        # thing.button = button.create_button(thing.name, thing.origin, thing.position, thing.size, thing.scale)
        # self.things.append(thing)


        self.update_task = taskMgr.add(self.update, "update")


    def test(self):
        print(test)

    def update(self, task):
        # time between frames
        dt = globalClock.getDt()

        mouse.update(dt)
        for thing in self.things:
            if thing.enabled:
                for script in thing.scripts:
                    try:
                        script.update(dt)
                    except:
                        pass

        return Task.cont


    def input(self, key):
        for thing in self.things:
            # if thing.enabled:
            for script in thing.scripts:
                try:
                    script.input(key)
                except:
                    pass


    def collision_point(point=(0,0,0)):
        return collision.point(point)


    def raycast(origin, direction, distance):
        return False

loadPrcFileData("", "window-title Panda Editor")

loadPrcFileData('', 'win-size %i %i' % screen_size)
# loadPrcFileData('', 'fullscreen true')
loadPrcFileData('', 'sync-video true')
loadPrcFileData('', 'show-frame-rate-meter true')
# loadPrcFileData('', 'win-size 720 480')

app = MyApp()
app.run()
