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
        self.editor_camera_script = load_script('scripts.editor_camera_script')
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



    #     text = load_prefab('text')
    #     text.parent = self.scene_list
    #     text.position = (0, -.1, 0)
    #     text.scale = (.9,.9,.9)
    #     t = 'test text'
    # #     t = '''zxcvb nmasd ghj qwetyutuoi phklz xcvbnma sdghjqwetyutuo iphkl xcvbnm
    # # asdgh jqwetyu tuoiphklzxcv bnma s ghjqw et yutu oiph klzxcvbnm asdgh jqwe tyut uoi phkl
    # # zxcvb nmasd ghj qwetyutuoi phklz xcvbnma sdghjqwetyutuo iphkl xcvbnm
    # # asdgh jqwetyu tuoiphklzxcv bnma s ghjqw et yutu oiph klzxcvbnm asdgh jqwe tyut uoi phkl
    # # zxcvb nmasd ghj qwetyutuoi phklz xcvbnma sdghjqwetyutuo iphkl xcvbnm
    # # asdgh jqwetyu tuoiphklzxcv bnma s ghjqw et yutu oiph klzxcvbnm asdgh jqwe tyut uoi phkl'''
    #     text.text = t
    #     # text.color = color.blue

# load model
        self.load_model_button = load_prefab('editor_button')
        self.load_model_button.is_editor = True
        self.load_model_button.parent = self
        self.load_model_button.name = 'load_model_button'
        self.load_model_button.origin = (0, .5)
        self.load_model_button.position = (0, .5, 0)
        self.load_model_button.scale = (.08, .05)
        self.load_model_button.color = color.panda_button
        self.load_model_button.text = 'load\nmodel'
        self.load_model_button.text_entity.x = 0
        self.menu_toggler = self.load_model_button.add_script('menu_toggler')

        self.model_list = load_prefab('filebrowser')
        self.model_list.is_editor = True
        self.model_list.parent = self
        self.model_list.position = (0,0)
        self.model_list.enabled = False
        self.model_list.file_types = ('.egg')
        self.model_list.path = os.path.join(os.path.dirname(scene.asset_folder), 'models')
        self.menu_toggler.target = self.model_list

# load sprites
        self.load_sprite_button = load_prefab('editor_button')
        self.load_sprite_button.is_editor = True
        self.load_sprite_button.parent = self
        self.load_sprite_button.name = 'load_sprite_button'
        self.load_sprite_button.origin = (0, .5)
        self.load_sprite_button.position = (.2, .5, 0)
        self.load_sprite_button.scale = (.08, .05)
        self.load_sprite_button.color = color.panda_button
        self.load_sprite_button.text = 'load\nsprite'
        self.load_sprite_button.text_entity.x = 0
        self.menu_toggler = self.load_sprite_button.add_script('menu_toggler')

        self.texture_list = load_prefab('filebrowser')
        self.texture_list.is_editor = True
        self.texture_list.parent = self
        self.texture_list.position = (0,0)
        self.texture_list.enabled = False
        self.texture_list.file_types = ('.png', '.jpg', '.psd', '.gif')
        self.texture_list.path = os.path.join(os.path.dirname(scene.asset_folder), 'textures')
        self.menu_toggler.target = self.texture_list

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
        self.toggle_button.position = (-.2, .5, 0)
        self.toggle_button.scale = (.08, .05)
        self.toggle_button.color = color.panda_button
        self.toggle_button.text = '2D/3D'
        self.toggle_button.text_entity.x = 0
        self.toggle_button.add_script('toggle_sideview')

        self.inspector = load_prefab('inspector')
        self.inspector.is_editor = True
        self.inspector.parent = self
        print('inspector', self.inspector)


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

            if self.enabled:
                camera.wrtReparentTo(self.camera_pivot)
                camera.position = self.editor_camera_script.position

                for e in scene.entities:
                    e.show()
                    if not e.is_editor:
                        e.editor_collider = 'box'
                        e.collider.stash()
                        e.collider.node_path.show()
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
