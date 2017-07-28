import sys
sys.path.append("..")
from pandaeditor import *
import os

class Editor(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'editor'
        self.is_editor = True
        self.parent = scene.ui.entity
        self.editor_camera = load_script('scripts.editor_camera')
        self.editor_camera.position = (0, -100, 0)
        scene.editor_camera = self.editor_camera

        self.camera_pivot = Entity()
        self.camera_pivot.is_editor = True
        camera.parent = self.camera_pivot

        self.cursor = Entity()
        self.cursor.is_editor = True
        self.cursor.model = 'circle'

        self.grid = load_prefab('panel')
        self.grid.name = 'grid'
        self.grid.parent = scene.render
        self.grid.position = (0, 0, 0)
        self.grid.rotation = (-90, 0, 0)
        self.grid.scale = (10, 10, 10)
        self.grid.collider = 'box'
        print(self.grid.collider.shape)
        self.grid.color = color.lime


        toolbar = load_prefab('panel')
        toolbar.name = 'toolbar'
        toolbar.parent = self
        toolbar.origin = (0, 0, .5)
        toolbar.position = (0, 0, .485)
        toolbar.scale = (1, 1, .025)
        toolbar.color = color.gray

        for i in range(4):
            button = load_prefab('button')
            button.name = 'toolbar button'
            button.parent = toolbar
            button.origin = (-.5, 0, .5)
            button.position = (-.487 + (i * .061), 0, 0)
            button.scale = (.06, 1, 1)
            button.color = color.orange
            # button.text = 'button'
            # button.text.color = color.black


        sidebar = load_prefab('panel')
        sidebar.name = 'sidebar'
        sidebar.parent = self
        sidebar.origin = (-.5, 0, -0.0)
        sidebar.position = (-.5, 0, 0)
        sidebar.scale = (.04, 1, .9)
        # sidebar.color = color.gray
        sidebar.color = color.black33
        # test.color = hsv_color(210, 1, 1)
        # print(color.hsv_color(90, 1, 1))

        self.scene_list = load_prefab('panel')
        self.scene_list.name = 'scene_list'
        self.scene_list.parent = self
        self.scene_list.scale = (.4, 1, .5)
        self.scene_list.color = color.black33
        self.scene_list.visible = False

        self.model_list = load_prefab('panel')
        self.model_list.name = 'model_list'
        self.model_list.scale = (.4, 1, .5)
        self.model_list.color = color.black33
        self.model_list.visible = False

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


        self.texture_list = load_prefab('filebrowser')
        # self.texture_list.collider = 'box'
        self.texture_list.parent = self
        # self.texture_list.scale = (1, 1, 1)
        self.texture_list.visible = False
        # print(scene.asset_folder)
        self.texture_list.file_types = ('.png', '.jpg', '.psd', '.gif')
        self.texture_list.path = os.path.join(os.path.dirname(scene.asset_folder), 'textures')



    def input(self, key):

        if key == 'tab':
            # print(inspect.currentframe().f_back.f_locals['self'])
            self.visible = not self.visible
            if self.visible:
                camera.position = self.editor_camera.position
                for e in scene.entities:
                    try:
                        e.collider.show()
                    except:
                        pass
            else:
                self.editor_camera.position = camera.position

        if self.visible:
            self.editor_camera.input(key)

        if key == 's':
            self.scene_list.visible = True
        if key == 's up':
            self.scene_list.visible = False
        if key == 'm':
            self.model_list.visible = True
        if key == 'm up':
            self.model_list.visible = False
        if key == 't':
            self.texture_list.visible = True
        if key == 't up':
            self.texture_list.visible = False
