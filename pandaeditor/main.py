# from pandastuff import *
from pandaeditor.pandastuff import *
from os import walk
import os
from panda3d.core import Camera


class PandaEditor(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        scene.reparentTo(self.render)
        scene.render = self.render
        application.base = base

        window.load_defaults()

        # camera
        camera.cam = base.camera
        camera.cam.reparentTo(camera)
        camera.parent = self.render
        camera.render = self.render
        camera.aspect_ratio = window.size[0] / window.size[1]
        camera.position = (0, 0, -20)
        scene.camera = camera
        camera.reparentTo(scene)
        camera.set_up()
        render.setAntialias(AntialiasAttrib.MAuto)

        # reapply screen effect to make it work in new resolution
        # print('adfaaaaaa:', application.base.win)
        # from direct.filter.CommonFilters import CommonFilters
        # filters = CommonFilters(application.base.win, application.base.cam)
        # filters.setAmbientOcclusion(
        #     numsamples=64,
        #     radius=0.1,
        #     amount=5.0,
        #     strength=0.05,
        #     falloff=0.000002
        # )

        # UI
        win = base.camNode.getDisplayRegion(0).getWindow()
        win.setClearColor(color.dark_gray)
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
        ui.is_editor = True
        ui.parent = ui_camera
        ui.model = 'quad'
        ui.scale = (ui_size * .5, ui_size * .5)
        # ui.color = color.white33
        if ui.model:
            ui.model.hide()
        scene.ui = ui
        camera.ui = ui


        # input
        base.buttonThrowers[0].node().setButtonDownEvent('buttonDown')
        base.buttonThrowers[0].node().setButtonUpEvent('buttonUp')
        self.dictionary = {
            'mouse1' : 'left mouse down',
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
            'arrow_right' : 'arrow right',
            'lcontrol' : 'left control',
            'rcontrol' : 'right control',
            'lshift' : 'left shift',
            'rshift' : 'right shift',
            'lalt' : 'left alt',
            'ralt' : 'right alt',
            'lcontrol up' : 'left control up',
            'rcontrol up' : 'right control up',
            'lshift up' : 'left shift up',
            'rshift up' : 'right shift up',
            'lalt up' : 'left alt up',
            'ralt up' : 'right alt up',
            'control-mouse1' : 'left mouse down',
            'control-mouse2' : 'middle mouse down',
            'control-mouse3' : 'right mouse down',
            'shift-mouse1' : 'left mouse down',
            'shift-mouse2' : 'middle mouse down',
            'shift-mouse3' : 'right mouse down',
            'alt-mouse1' : 'left mouse down',
            'alt-mouse2' : 'middle mouse down',
            'alt-mouse3' : 'right mouse down'
            }
        self.accept('buttonDown', self.input)
        self.accept('buttonUp', self.input_up)

        base.disableMouse()
        mouse.mouse_watcher = base.mouseWatcherNode
        mouse.enabled = True

        scene.set_up()

        # t = load_scene('minecraft_clone')
        # count_lines(inspect.getfile(t.__class__))

        # start game if there is no editor
        for e in scene.entities:
            try:
                e.start()
            except:
                pass
            try:
                for s in e:
                    try:
                        s.start()
                    except:
                        pass
            except:
                pass

        self.update_task = taskMgr.add(self.update, "update")



    def update(self, task):
        # time between frames
        dt = globalClock.getDt()

        mouse.update(dt)
        if scene.editor and scene.editor.enabled:
            scene.editor.update(dt)
        # except: pass

        for entity in scene.entities:
            if entity.enabled:
                try:
                    entity.update(dt)
                except:
                    pass

                for script in entity.scripts:
                    try:
                        script.update(dt)
                    except:
                        pass

        return Task.cont

    def input_up(self, key):
        if key is not 'wheel_up' and key is not 'wheel_down':
            key += ' up'
            self.input(key)


    def input(self, key):
        if key == 'f11':
            window.fullscreen = not window.fullscreen

        try:
            key = self.dictionary[key]
        except:
            pass
        try:
            key = key.replace('control-', '')
        except:
            pass
        try:
            key = key.replace('shift-', '')
        except:
            pass
        try:
            key = key.replace('alt-', '')
        except:
            pass


        try:
            if scene.editor and scene.editor.enabled:
                scene.editor.input(key)
        except: pass
        try: mouse.input(key)
        except: pass
        try: keys.input(key)
        except: pass

        for entity in scene.entities:
            if entity.enabled and entity is not scene.editor:
                try: entity.input(key)
                except: pass
                for script in entity.scripts:
                    try: script.input(key)
                    except: pass


    def load_editor(self):
        scene.editor = load_script('editor')


if __name__ == '__main__':
    app = PandaEditor()
    app.load_editor()
    # load_scene('minecraft_clone')
    window.fps_counter = True
    print('scene entity', scene.entity)
    app.run()
