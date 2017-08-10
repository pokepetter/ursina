from pandaeditor import *
from os import walk
import os



class PandaEditor(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        scene.reparentTo(self.render)
        scene.app = self
        scene.render = self.render
        scene.asset_folder = __file__

        # camera
        # aspect_ratio = screen_size[0] / screen_size[1]
        # lens = OrthographicLens()
        # orthographicSize = 20
        # lens.setFilmSize(orthographicSize * aspect_ratio, orthographicSize)
        # lens = PerspectiveLens()
        # lens.setFocalLength(50)

        # lens.setAspectRatio(aspect_ratio)
        # base.cam.node().setLens(lens)
        camera.cam = base.camera
        camera.cam.reparentTo(camera)
        # camera.lens = lens
        # camera.lens_node = LensNode('lens_node', camera.lens)
        camera.parent = self.render
        camera.render = self.render
        camera.aspect_ratio = screen_size[0] / screen_size[1]
        # camera.fov = 40
        # camera.near_clip_plane = 0.01
        # camera.far_clip_plane = 100
        camera.position = (0, -20, 0)
        camera.rotation = (0,0,0)
        scene.camera = camera
        camera.reparentTo(scene)


        # input
        base.buttonThrowers[0].node().setButtonDownEvent('buttonDown')
        base.buttonThrowers[0].node().setButtonUpEvent('buttonUp')
        self.dictionary = {'mouse1' : 'left mouse down',
                    'mouse1 up' : 'left mouse up',
                    'mouse2' : 'middle mouse down',
                    'mouse2 up' : 'middle mouse up',
                    'mouse3' : 'right mouse down',
                    'mouse3 up' : 'right mouse up',
                    'wheel_up' : 'scroll up',
                    'wheel_down' : 'scroll down',
                    'arrow_left' : 'arrow left',
                    'arrow_up' : 'arrow up',
                    'arrow_down' : 'arrow down',
                    'arrow_right' : 'arrow right'}
        self.accept('buttonDown', self.input)
        self.accept('buttonUp', self.input_up)
        # self.accept('lalt', self.input, ['left alt'])

        base.disableMouse()
        mouse.mouse_watcher = base.mouseWatcherNode


        # UI
        ui_entity = Entity()
        ui_entity.name = 'ui'
        ui_entity.parent = camera.cam
        ui_entity.position = (0, 50, 0)
        ui_entity.model = 'quad'
        ui = ui_entity.add_script('ui')
        ui.entity = ui_entity
        ui.fit_to_screen()
        ui_entity.model.hide()
        scene.ui = ui


        scene.editor = load_script('editor')

        self.update_task = taskMgr.add(self.update, "update")



    def update(self, task):
        # time between frames
        dt = globalClock.getDt()

        mouse.update(dt)
        try: scene.editor.editor_camera.update(dt)
        except: pass

        for entity in scene.entities:
            if entity.enabled:
                for script in entity.scripts:
                    try:
                        script.update(dt)
                    except:
                        pass

        return Task.cont

    def input_up(self, key):
        if key != 'wheel_up' and key != 'wheel_down':
            key += ' up'
            self.input(key)


    def input(self, key):
        try: key = self.dictionary[key]
        except: pass

        try: scene.editor.input(key)
        except: pass
        try: mouse.input(key)
        except: pass

        for entity in scene.entities:
            # if entity.enabled:
            for script in entity.scripts:
                try: script.input(key)
                except: pass


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

app = PandaEditor()
app.run()
