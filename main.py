from pandaeditor import *

from os import walk
import os
from editor_camera import EditorCamera

class PandaEditor(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)

        scene.app = self
        scene.render = self.render

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
        scene.camera = camera


        # input
        base.buttonThrowers[0].node().setKeystrokeEvent('keystroke')
        self.accept('keystroke', self.input)
        self.accept('tab', self.input, ['tab'])

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

        # import ast
        # import importlib
        # import importlib.util
        # #
        # self_directory = os.path.dirname(os.path.abspath(__file__))
        # scenes_directory = os.path.join(self_directory, 'scenes')
        # scene_files = []
        # for root, dirs, files in os.walk(scenes_directory):
        #     for filename in files:
        #         if filename.lower().endswith('.py'):
        #             print('script:', filename)
        #
        #             # spec = importlib.util.spec_from_file_location("module.name", os.path.join(scenes_directory, filename))
        #             # foo = importlib.util.module_from_spec(spec)
        #             # spec.loader.exec_module(foo)
        #             # module = importlib.import_module(os.path.join(scenes_directory, filename), package=None)
        #
        #             # class_names = inspect.getmembers(sys.modules[module_name], inspect.isclass)
        #             # scene_files.append(filename)
        #             with open(os.path.join(scenes_directory, filename)) as f:
        #                 p = ast.parse(f.read())
        #                 classes = [node.name for node in ast.walk(p) if isinstance(node, ast.ClassDef)]
        #                 for c in classes:
        #                     print('class:', c)
        #                 #     scene_files.append(c)




        # scene_script.parent = self


        # try:
        #     with open(scene_path, 'r') as scene_file:
        #         for line in scene_file:
        #             print(line)
        # except:
        #     print(scene_path, 'could not be loaded')


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
        self.editor_camera = Entity()
        self.editor_camera.name = 'editor_camera'
        self.editor_camera.parent = self.render
        # self.editor_camera.add_script(EditorCamera)
        camera.position = (0,-100,0)
        camera.rotation = (0,0,0)
        scene.editor_camera = self.editor_camera


        # UI
        ui_entity = Entity()
        ui_entity.name = 'ui'
        ui_entity.parent = self.render
        ui_entity.position = (0, -50, 0)
        ui_entity.model = loader.loadModel('models/quad.egg')
        ui = ui_entity.add_script('ui')
        ui.entity = ui_entity
        ui.fit_to_screen()
        ui_entity.model.detachNode()
        scene.ui = ui


        # self.panel = load_scene('editor')



        # # ui button
        # button_entity = Entity()
        # button_entity.name = 'button'
        # button_entity.parent = ui_entity.node_path
        # button_entity.model = loader.loadModel('models/quad_rounded.egg')
        # # tex = loader.loadTexture('textures/winter_forest.png')
        # # button_entity.model.setTexture(tex, 1)
        #
        # button_entity.position = (0.25, 0, 0.25)
        # button_entity.scale = (.25, 1, 0.5)
        # # button_entity.origin = (-1, 0, 0)
        # button_entity.collision = True
        # button_entity.collider = (button_entity.node_path.getPos(self.render), (0,0,0),
        #                 (button_entity.model.getScale(self.render)[0] /4, 1,
        #                 button_entity.model.getScale(self.render)[2] /4))
        #
        # button_script = button_entity.add_script('button')
        # button_script.ui = scene.ui
        # button_script.color = color.gray
        # button_script.set_up()
        # scene.entities.append(button_entity)
        # # -------------


        entity = Entity()
        entity.name = 'empty'
        entity.parent = self.render
        entity.model = self.loader.loadModel('models/cube.egg')
        entity.model.reparentTo(entity.node_path)
        entity.position = (0,0,0)
        # entity.scale = (0.5,0.5,0.5)
        # entity.scale = .1
        # entity.collision = True
        # entity.collider
        # entity.add_script('player')
        entity.add_script(EditorCamera)
        scene.entities.append(entity)
        prev_entity = entity

        # entity = Entity()
        # entity.name = 'empty'
        # entity.parent = prev_entity.node_path
        # entity.model = self.loader.loadModel('models/cube.egg')
        # entity.model.reparentTo(entity.node_path)
        # entity.position = (3,0,0)
        # entity.scale = (2,2,2)
        # button_script = entity.add_script(Button)
        # button_script.ui = ui_script
        # button_script.color = color.gray
        # button_script.set_up()
        # scene.entities.append(entity)
        # print(entity.node_path.getPos(self.render))



        self.update_task = taskMgr.add(self.update, "update")


    def test(self):
        print(test)

    def update(self, task):
        # time between frames
        dt = globalClock.getDt()

        mouse.update(dt)
        try: editor_camera.update(dt)
        except: pass

        for entity in scene.entities:
            if entity.enabled:
                for script in entity.scripts:
                    try:
                        script.update(dt)
                    except:
                        pass

        return Task.cont


    def input(self, key):
        try: scene.ui.input(key)
        except: pass
        try: scene.editor_camera.input(key)
        except: pass

        for entity in scene.entities:
            # if entity.enabled:
            for script in entity.scripts:
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

app = PandaEditor()
app.run()
