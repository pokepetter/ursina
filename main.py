from pandaeditor import *
from os import walk
import os
from panda3d.core import Camera


class PandaEditor(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        scene.reparentTo(self.render)
        scene.app = self
        scene.base = base
        scene.render = self.render
        scene.asset_folder = os.path.dirname(__file__)

        window.load_defaults()

        #camera
        camera.base = base
        camera.cam = base.camera
        camera.cam.reparentTo(camera)
        camera.parent = self.render
        camera.render = self.render
        camera.aspect_ratio = window.size[0] / window.size[1]
        camera.position = (0, 0, -20)
        scene.camera = camera
        camera.reparentTo(scene)
        camera.set_up()

        # UI
        win = base.camNode.getDisplayRegion(0).getWindow()
        ui_display_region = win.makeDisplayRegion()
        ui_display_region.setSort(20)

        ui_size = 40
        ui_camera = NodePath(Camera('ui_camera'))
        lens = OrthographicLens()
        lens.setFilmSize(ui_size * .5 * camera.aspect_ratio, ui_size * .5)
        lens.setNearFar(-1000, 1000)
        ui_camera.node().setLens(lens)
        camera.ui_lens_node = LensNode('ui_lens_node', lens)

        ui_render = NodePath('ui_render')
        ui_render.setDepthTest(0)
        ui_render.setDepthWrite(0)
        ui_camera.reparentTo(ui_render)
        ui_display_region.setCamera(ui_camera)
        scene.ui_camera = ui_camera
        # ui_camera.hide()

        ui = Entity()
        ui.name = 'ui'
        ui.parent = ui_camera
        ui.model = 'quad'
        ui.scale = (ui_size * camera.aspect_ratio * .5, ui_size * .5)
        ui.color = color.white33
        if ui.model:
            ui.model.hide()
        scene.ui = ui
        camera.ui = ui

        win.setClearColor(color.dark_gray)


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
        mouse.enabled = True


        scene.editor = load_script('editor')

        self.update_task = taskMgr.add(self.update, "update")



    def update(self, task):
        # time between frames
        dt = globalClock.getDt()

        mouse.update(dt)
        if scene.editor:
            scene.editor.update(dt)
        # except: pass

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
        if key == 'f11':
            window.fullscreen = not window.fullscreen

        try: key = self.dictionary[key]
        except: pass

        if key == 'u':
            destroy(scene.editor)
            scene.editor = load_script('editor')

        try:
            scene.editor.input(key)
        except: pass
        try: mouse.input(key)
        except: pass

        for entity in scene.entities:
            if entity.enabled:
                for script in entity.scripts:
                    try: script.input(key)
                    except: pass


    def collision_point(point=(0,0,0)):
        return collision.point(point)


    def raycast(origin, direction, distance):
        return 0



app = PandaEditor()
app.run()
