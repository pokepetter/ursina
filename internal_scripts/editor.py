import sys
sys.path.append("..")
from pandaeditor import *
import os
from panda3d.bullet import BulletDebugNode

class Editor(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'editor'
        self.is_editor = True
        self.parent = scene.ui
        self.editor_camera_script = load_script('editor_camera_script')
        self.editor_camera_script.position = (0, 0, -100)
        scene.editor_camera_script = self.editor_camera_script

        self.camera_pivot = Entity()
        self.camera_pivot.is_editor = True
        camera.parent = self.camera_pivot

        self.selection = list()

        self.transform_gizmo = load_prefab('transform_gizmo')
        self.transform_gizmo.name = 'transform_gizmo'
        self.transform_gizmo.is_editor = True
        self.transform_gizmo.parent = scene.render


        self.grid = load_prefab('panel')
        self.grid.is_editor = True
        self.grid.name = 'grid'
        self.grid.parent = scene.render
        self.grid.position = (0, 0, 0)
        self.grid.rotation = (-90, 0, 0)
        self.grid.scale = (10, 10, 10)
        self.grid.color = color.lime

# top menu
        self.top_menu = Entity()
        self.top_menu.parent = self
        # self.top_menu.origin = (.5, .5)
        self.top_menu.position = window.top
        self.layout_group = self.top_menu.add_script('grid_layout')
        self.layout_group.origin = (0, .5)
        self.layout_group.spacing = (.001, 0)

# play button
        self.play_button = load_prefab('editor_button')
        self.play_button.is_editor = True
        self.play_button.parent = self.top_menu
        self.play_button.origin = (0, .5)
        self.play_button.name = 'play_button'
        self.play_button.scale = (.1, .05)
        self.play_button.color = color.panda_button
        self.play_button.text = 'play'
        # self.menu_toggler = self.play_button.add_script('menu_toggler')

        self.pause_button = load_prefab('editor_button')
        self.pause_button.is_editor = True
        self.pause_button.parent = self.top_menu
        self.pause_button.origin = (0, .5)
        self.pause_button.name = 'pause_button'
        self.pause_button.scale = (.1, .05)
        self.pause_button.color = color.panda_button
        self.pause_button.text = 'pause'
        # self.menu_toggler = self.play_button.add_script('menu_toggler')

        self.layout_group.update_grid()

# load menu
        self.load_menu_parent = Entity()
        self.load_menu_parent.parent = self
        # self.load_menu_parent.origin = (.5, .5)
        self.load_menu_parent.position = window.top_right
        self.load_menu_parent.y -= .1
        self.layout_group = self.load_menu_parent.add_script('grid_layout')
        self.layout_group.origin = (.5, .5)
        self.layout_group.max_x = 1
        self.layout_group.spacing = (0, .001)

# # new scene
#         self.new_scene_button = load_prefab('editor_button')
#         self.new_scene_button.is_editor = True
#         self.new_scene_button.parent = self.load_menu_parent
#         self.new_scene_button.name = 'new_scene_button'
#         self.new_scene_button.scale = (.1, .05)
#         self.new_scene_button.color = color.panda_button
#         self.new_scene_button.text = 'new scene'
#         self.new_scene_button.text_entity.origin = (0,0)
#         # self.menu_toggler = self.new_scene_button.add_script('menu_toggler')

# load scene
        self.load_scene_button = load_prefab('editor_button')
        self.load_scene_button.is_editor = True
        self.load_scene_button.parent = self.load_menu_parent
        self.load_scene_button.name = 'load_scene_button'
        self.load_scene_button.scale = (.1, .05)
        self.load_scene_button.color = color.panda_button
        self.load_scene_button.text = 'scenes'
        self.load_scene_button.text_entity.origin = (.5, 0)
        self.load_scene_button.text_entity.x = .4
        self.menu_toggler = self.load_scene_button.add_script('menu_toggler')

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.is_editor = True
        self.filebrowser.parent = self
        self.filebrowser.position = (0,0)
        self.filebrowser.enabled = False
        self.filebrowser.file_types = ('.py')
        self.filebrowser.path = os.path.join(os.path.dirname(scene.asset_folder), 'scenes')
        self.filebrowser.button_type = 'load_scene_button'
        self.menu_toggler.target = self.filebrowser

# load prefab
        self.load_prefab_button = load_prefab('editor_button')
        self.load_prefab_button.is_editor = True
        self.load_prefab_button.parent = self.load_menu_parent
        self.load_prefab_button.name = 'load_prefab_button'
        self.load_prefab_button.scale = (.1, .05)
        self.load_prefab_button.color = color.panda_button
        self.load_prefab_button.text = 'prefab'
        self.menu_toggler = self.load_prefab_button.add_script('menu_toggler')

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.is_editor = True
        self.filebrowser.parent = self
        self.filebrowser.position = (0,0)
        self.filebrowser.enabled = False
        self.filebrowser.file_types = ('.py')
        self.filebrowser.path = os.path.join(os.path.dirname(scene.asset_folder), 'prefabs')
        self.filebrowser.button_type = 'load_prefab_button'
        self.menu_toggler.target = self.filebrowser

# load model
        self.load_model_button = load_prefab('editor_button')
        self.load_model_button.is_editor = True
        self.load_model_button.parent = self.load_menu_parent
        self.load_model_button.name = 'load_model_button'
        self.load_model_button.scale = (.1, .05)
        self.load_model_button.color = color.panda_button
        self.load_model_button.text = 'model'
        self.menu_toggler = self.load_model_button.add_script('menu_toggler')

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.is_editor = True
        self.filebrowser.parent = self
        self.filebrowser.position = (0,0)
        self.filebrowser.enabled = False
        self.filebrowser.file_types = ('.egg')
        self.filebrowser.path = os.path.join(os.path.dirname(scene.asset_folder), 'models')
        self.filebrowser.button_type = 'load_model_button'
        self.menu_toggler.target = self.filebrowser

# load primitive
        self.load_primitive_button = load_prefab('editor_button')
        self.load_primitive_button.is_editor = True
        self.load_primitive_button.parent = self.load_menu_parent
        self.load_primitive_button.name = 'load_primitive_button'
        self.load_primitive_button.scale = (.1, .05)
        self.load_primitive_button.color = color.panda_button
        self.load_primitive_button.text = 'primitive'
        self.menu_toggler = self.load_primitive_button.add_script('menu_toggler')

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.is_editor = True
        self.filebrowser.parent = self
        self.filebrowser.position = (0,0)
        self.filebrowser.enabled = False
        self.filebrowser.file_types = ('.egg')
        self.filebrowser.path = os.path.join(os.path.dirname(scene.asset_folder), 'pandaeditor/internal_models')
        self.filebrowser.button_type = 'load_model_button'
        self.menu_toggler.target = self.filebrowser

# load sprites
        self.load_sprite_button = load_prefab('editor_button')
        self.load_sprite_button.is_editor = True
        self.load_sprite_button.parent = self.load_menu_parent
        self.load_sprite_button.name = 'load_sprite_button'
        self.load_sprite_button.scale = (.1, .05)
        self.load_sprite_button.color = color.panda_button
        self.load_sprite_button.text = 'sprite'
        self.menu_toggler = self.load_sprite_button.add_script('menu_toggler')

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.is_editor = True
        self.filebrowser.parent = self
        self.filebrowser.position = (0,0)
        self.filebrowser.enabled = False
        self.filebrowser.file_types = ('.png', '.jpg', '.psd', '.gif')
        self.filebrowser.path = os.path.join(os.path.dirname(scene.asset_folder), 'textures')
        self.filebrowser.button_type = 'load_texture_button'
        self.menu_toggler.target = self.filebrowser

        self.layout_group.update_grid()

# entity list
        self.entity_list = load_prefab('entity_list')
        self.entity_list.parent = self
        self.entity_list.populate()

# inspector
        self.inspector = load_prefab('inspector')
        self.inspector.parent = self

# temp, make into canvas prefab
        self.ui_canvas = Entity()
        # self.ui_canvas.parent = camera.ui
        self.ui_canvas.scale = (1, 1)
        self.ui_canvas.model = 'canvas'
        self.ui_canvas.color = color.white33
        self.ui_canvas.add_script('canvas')

# 2D / 3D toggle
        self.toggle_button = load_prefab('editor_button')
        self.toggle_button.is_editor = True
        self.toggle_button.parent = self
        self.toggle_button.name = 'toggle_button'
        self.toggle_button.origin = (0, .5)
        self.toggle_button.position = (-.4, .5)
        self.toggle_button.scale = (.1, .05)
        self.toggle_button.color = color.panda_button
        self.toggle_button.text = '2D/3D'
        self.toggle_button.text_entity.x = 0
        self.toggle_button.add_script('toggle_sideview')



# exit button
        self.exit_button = load_prefab('editor_button')
        self.exit_button.is_editor = True
        self.exit_button.parent = self
        self.exit_button.name = 'toggle_button'
        self.exit_button.origin = (.5, .5)
        self.exit_button.position = window.top_right
        self.exit_button.scale = (.06, .03)
        self.exit_button.color = color.panda_button
        self.exit_button.text = 'X'
        self.exit_button.text_entity.x = 0
        # self.exit_button.add_script('toggle_sideview')


        # # testing
        # self.cube = Entity()
        # self.cube.name = 'cube'
        # # self.cube.model = 'cube'
        # # self.cube.color = color.red
        # self.cube.add_script('test')
        # # print(self.cube.scripts)
        # # return
        # self.selected = self.cube
        # random.seed(0)
        # for z in range(4):
        #     for x in range(4):
        #         c = Entity()
        #         c.name = 'cube'
        #         c.model = 'cube'
        #         c.color = color.hsv_color(x * 30, 1, (z + 1) / 10)
        #         c.parent = self.cube
        #         c.position = (x, random.uniform(0, 1), z)
        #         c.scale *= .95
        #
        #         d = Entity()
        #         d.name = 'cube1'
        #         d.model = 'cube'
        #         d.parent = c
        #         d.scale *= .2
        #         d.y = 1
        #         d.color = color.orange
        #
        # c.color = color.blue




    def update(self, dt):
        self.editor_camera_script.update(dt)
        self.transform_gizmo.update(dt)
        # self.inspector.update(dt)

    def input(self, key):
        if key == 'i':
            save_prefab(self.cube)
        if key == 'o':
            scene.clear()
        if key == 'p':
            print('p')
            e = load_scene('cube_1')
            # e = load_script('cube_1')
            e.parent = scene.render
            print('loaded')

        if key == 'h':
            self.show_colliders = not self.show_colliders
            if self.show_colliders:
                self.debugNP.show()
            else:
                self.debugNP.hide()

        if key == 'tab':
            self.enabled = not self.enabled

            # enable editor
            if self.enabled:
                camera.wrtReparentTo(self.camera_pivot)
                camera.position = self.editor_camera_script.position

                for e in scene.entities:
                    e.show()
                    if not e.is_editor:
                        e.editor_collider = 'box'
                        e.collider.stash()
                        e.collider.node_path.show()
            # disable editor
            else:
                self.editor_camera_script.position = camera.position
                camera.wrtReparentTo(scene.render)
                for e in scene.entities:
                    try:
                        if e.editor_collider:
                            e.editor_collider.stash()
                        e.collider.unstash()
                    except:
                        pass

                    try:
                        e.start()
                    except:
                        pass
                    for s in e.scripts:
                        try:
                            print('script:', s)
                            s.start()
                        except:
                            pass



        if self.enabled:
            self.editor_camera_script.input(key)


        if key == 's':
            print('s')
            save_prefab('name')
        #     self.scene_list.visible = True
        # if key == 's up':
        #     self.scene_list.visible = False


    def on_disable(self):
        self.transform_gizmo.enabled = False
        self.grid.enabled = False
        # self.enabled = False

    def on_enable(self):
        # self.enabled = True
        self.transform_gizmo.enabled = True
        self.grid.enabled = True
