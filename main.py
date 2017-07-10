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
        self.clip_plane_near = 0.01
        self.clip_plane_far = 100
        # lens = OrthographicLens()
        lens = PerspectiveLens()
        lens.setFocalLength(50)
        aspect_ratio = screen_size[0] / screen_size[1]
        lens.setAspectRatio(aspect_ratio)
        base.cam.node().setLens(lens)
        camera.cam = base.camera
        camera.lens = lens
        camera.render = self.render
        camera.fov = 40
        camera.near_clip_plane = 0.01
        camera.far_clip_plane = 100
        # camera.focal_length = 50


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
        self.gameobjects = []
        self.scene = Gameobject()

        self.editor_camera = Gameobject()
        self.editor_camera.name = 'editor_camera'
        self.editor_camera.parent = self.render
        # self.editor_camera.add_script(EditorCamera)

        # camera.y = -100
        camera.position = (0,-100,0)
        camera.rotation = (0,0,0)
        self.gameobjects.append(self.editor_camera)

        # UI
        ui_gameobject = Gameobject()
        ui_gameobject.name = 'ui'
        ui_gameobject.parent = self.render
        ui_gameobject.position = (0, -50, 0)
        # ui_gameobject.node_path.setPos(Vec3(0,-2,0))
        ui_gameobject.model = loader.loadModel('models/quad_rounded.egg')
        ui_gameobject.model.hide()
        ui_script = ui_gameobject.add_script(UI)
        ui_script.fit_to_screen()
        self.gameobjects.append(ui_gameobject)


        for i in range(2):
            button = Gameobject()
            button.name = 'button'
            button.parent = ui_gameobject.node_path
            button.model = loader.loadModel('models/quad_rounded.egg')
            button.position = (0.25 * i, 0, 0.0)
            button.scale = (.25, 1, 0.5)
            # button.origin = (-1, 0, 0)
            button.collision = True
            button.collider = (button.node_path.getPos(self.render), (0,0,0),
                            (button.model.getScale(self.render)[0] /4, 1,
                            button.model.getScale(self.render)[2] /4))

            button_script = button.add_script(Button)
            button_script.ui = ui_script
            button_script.color = color.gray
            button_script.set_up()
            self.gameobjects.append(button)


        # print(button.node_path.getScale(self.render))



        # gameobject = Gameobject()
        # gameobject.name = 'empty'
        # gameobject.parent = self.render
        # gameobject.model = self.loader.loadModel('models/cube.egg')
        # gameobject.model.reparentTo(gameobject.node_path)
        # gameobject.position = button.collider[0]
        # gameobject.scale = button.collider[2]


        gameobject = Gameobject()
        gameobject.name = 'empty'
        gameobject.parent = self.render
        gameobject.model = self.loader.loadModel('models/cube.egg')
        gameobject.model.reparentTo(gameobject.node_path)
        gameobject.position = (0,0,0)
        # gameobject.scale = (0.5,0.5,0.5)
        # gameobject.scale = .1
        # gameobject.collision = True
        # gameobject.collider
        # gameobject.add_script('player')
        gameobject.add_script(EditorCamera)
        self.gameobjects.append(gameobject)
        prev_gameobject = gameobject

        # gameobject = Gameobject()
        # gameobject.name = 'empty'
        # gameobject.parent = prev_gameobject.node_path
        # gameobject.model = self.loader.loadModel('models/cube.egg')
        # gameobject.model.reparentTo(gameobject.node_path)
        # gameobject.position = (3,0,0)
        # gameobject.scale = (2,2,2)
        # button_script = gameobject.add_script(Button)
        # button_script.ui = ui_script
        # button_script.color = color.gray
        # button_script.set_up()
        # self.gameobjects.append(gameobject)
        # print(gameobject.node_path.getPos(self.render))



        # create button
        # gameobject = gameobject()
        # gameobject.name = 'button'
        # gameobject.origin = (-1,0,-1)
        # gameobject.position = (0 * aspect_ratio ,0, 0)
        # gameobject.scale = 0.04
        # gameobject.size = (500,0,512)
        # # button.collision = True
        # gameobject.button = button.create_button(gameobject.name, gameobject.origin, gameobject.position, gameobject.size, gameobject.scale)
        # self.gameobjects.append(gameobject)


        self.update_task = taskMgr.add(self.update, "update")


    def test(self):
        print(test)

    def update(self, task):
        # time between frames
        dt = globalClock.getDt()

        mouse.update(dt)
        for gameobject in self.gameobjects:
            if gameobject.enabled:
                for script in gameobject.scripts:
                    try:
                        script.update(dt)
                    except:
                        pass

        return Task.cont


    def input(self, key):
        for gameobject in self.gameobjects:
            # if gameobject.enabled:
            for script in gameobject.scripts:
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
