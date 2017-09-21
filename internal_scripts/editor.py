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


        self.toolbar = Entity()
        self.toolbar.parent = self
        self.layout_group = self.toolbar.add_script('grid_layout')
        self.layout_group.update_grid()
        # self.layout_group.origin = (0, 0)
        print('layout group:', self.layout_group)
        # self.layout_group.overflow = True
        # self.layout_group.spacing = (0.1, 0)

# load scene
        self.load_scene_button = load_prefab('editor_button')
        self.load_scene_button.is_editor = True
        self.load_scene_button.parent = self.toolbar
        self.load_scene_button.name = 'load_scene_button'
        self.load_scene_button.origin = (0, .5)
        self.load_scene_button.position = (-.12, .5)
        self.load_scene_button.scale = (.06, .06)
        self.load_scene_button.color = color.panda_button
        self.load_scene_button.text = 'scene'
        self.load_scene_button.text_entity.x = 0
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
        self.load_prefab_button.parent = self.toolbar
        self.load_prefab_button.name = 'load_prefab_button'
        self.load_prefab_button.origin = (0, .5)
        self.load_prefab_button.position = (-.06, .5)
        self.load_prefab_button.scale = (.06, .06)
        self.load_prefab_button.color = color.panda_button
        self.load_prefab_button.text = 'prefab'
        self.load_prefab_button.text_entity.x = 0
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
        self.load_model_button.parent = self.toolbar
        self.load_model_button.name = 'load_model_button'
        self.load_model_button.origin = (0, .5)
        self.load_model_button.position = (0, .5)
        self.load_model_button.scale = (.06, .06)
        self.load_model_button.color = color.panda_button
        self.load_model_button.text = 'model'
        self.load_model_button.text_entity.x = 0
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
        self.load_primitive_button.parent = self.toolbar
        self.load_primitive_button.name = 'load_primitive_button'
        self.load_primitive_button.origin = (0, .5)
        self.load_primitive_button.position = (.06, .5)
        self.load_primitive_button.scale = (.06, .06)
        self.load_primitive_button.color = color.panda_button
        self.load_primitive_button.text = 'primitive'
        self.load_primitive_button.text_entity.x = 0
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
        self.load_sprite_button.parent = self.toolbar
        self.load_sprite_button.name = 'load_sprite_button'
        self.load_sprite_button.origin = (0, .5)
        self.load_sprite_button.position = (.12, .5)
        self.load_sprite_button.scale = (.06, .06)
        self.load_sprite_button.color = color.panda_button
        self.load_sprite_button.text = 'load\nsprite'
        self.load_sprite_button.text_entity.x = 0
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



# entity list
        self.entity_list = load_prefab('entity_list')
        self.entity_list.is_editor = True
        self.entity_list.parent = self
        self.entity_list.populate()

# 2D / 3D toggle
        self.toggle_button = load_prefab('editor_button')
        self.toggle_button.is_editor = True
        self.toggle_button.parent = self
        self.toggle_button.name = 'toggle_button'
        self.toggle_button.origin = (0, .5)
        self.toggle_button.position = (-.4, .5)
        self.toggle_button.scale = (.06, .06)
        self.toggle_button.color = color.panda_button
        self.toggle_button.text = '2D/3D'
        self.toggle_button.text_entity.x = 0
        self.toggle_button.add_script('toggle_sideview')

        self.inspector = load_prefab('inspector')
        self.inspector.is_editor = True
        self.inspector.parent = self
        print('inspector', self.inspector)



    def update(self, dt):
        self.editor_camera_script.update(dt)
        self.transform_gizmo.update(dt)

    def input(self, key):
        # if key == 'i':
        #     self.entity_list.populate()

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
                    # print(e)
                    # try:
                    #     for s in e.scripts:
                    #         if s.is_editor:
                    #             e.scripts.remove(s)
                    #     # print('scripts', e.scripts)
                    # except:
                    #     pass
                    try:
                        if e.editor_collider:
                            e.editor_collider.stash()
                        print('stashed')
                        e.collider.unstash()
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
        self.visible = False

    def on_enable(self):
        self.visible = True
        self.transform_gizmo.enabled = True
        self.grid.enabled = True
