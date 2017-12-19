import sys
sys.path.append("..")
from pandaeditor import *
import os
from panda3d.bullet import BulletDebugNode
from types import MethodType
import debugwindow

class Editor(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'editor'
        self.is_editor = True
        self.parent = scene.ui

        self.trash = NodePath('trash')
        self.selection = list()

        self.editor_camera_script = load_script('editor_camera_script')
        self.editor_camera_script.position = (0, 0, -100)
        scene.editor_camera_script = self.editor_camera_script

        self.camera_pivot = Entity()
        self.camera_pivot.is_editor = True
        self.camera_pivot.name = 'camera_pivot'
        self.camera_pivot.parent = scene.render
        self.camera_pivot.is_editor = True
        camera.parent = self.camera_pivot


        self.transform_gizmo = load_prefab('transform_gizmo')
        self.transform_gizmo.name = 'transform_gizmo'
        self.transform_gizmo.is_editor = True
        self.transform_gizmo.parent = scene.render


        self.grid = Entity()
        self.grid.model = 'cube'
        self.grid.is_editor = True
        self.grid.name = 'grid_x'
        self.grid.parent = scene.render
        self.grid.position = (0, 0, 0)
        self.grid.scale = (10, 0, .02)
        self.grid.color = color.orange

        self.grid = Entity()
        self.grid.model = 'cube'
        self.grid.is_editor = True
        self.grid.name = 'grid_z'
        self.grid.parent = scene.render
        self.grid.position = (0, 0, 0)
        self.grid.rotation = (0, 90, 0)
        self.grid.scale = (10, 0, .02)
        self.grid.color = color.lime

# top menu
        self.top_menu = Entity()
        self.top_menu.parent = self
        self.top_menu.position = window.top
        self.layout_group = self.top_menu.add_script('grid_layout')
        self.layout_group.origin = (0, .5)
        self.layout_group.spacing = (.001, 0)

# play button
        self.play_button = load_prefab('editor_button')
        self.play_button.parent = self.top_menu
        self.play_button.origin = (0, .5)
        self.play_button.name = 'play_button'
        self.play_button.scale = (.1, .05)
        self.play_button.text = 'play'
        # self.menu_toggler = self.play_button.add_script('menu_toggler')

        self.pause_button = load_prefab('editor_button')
        self.pause_button.parent = self.top_menu
        self.pause_button.origin = (0, .5)
        self.pause_button.name = 'pause_button'
        self.pause_button.scale = (.1, .05)
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
#         self.new_scene_button.text = 'new scene'
#         self.new_scene_button.text_entity.origin = (0,0)
#         # self.menu_toggler = self.new_scene_button.add_script('menu_toggler')

# load scene
        self.load_scene_button = load_prefab('editor_button')
        self.load_scene_button.parent = self.load_menu_parent
        self.load_scene_button.name = 'load_scene_button'
        self.load_scene_button.scale = (.1, .05)
        self.load_scene_button.text = 'scenes'
        self.menu_toggler = self.load_scene_button.add_script('menu_toggler')
        self.load_scene_button.add_script('open_in_file_explorer')
        self.load_scene_button.open_in_file_explorer.path = Filename.toOsSpecific(application.internal_scene_folder)

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.parent = self
        self.filebrowser.position = (0,0)
        self.filebrowser.enabled = False
        self.filebrowser.file_types = ('.py')
        self.filebrowser.path = application.scene_folder
        self.filebrowser.button_type = 'load_scene_button'
        self.menu_toggler.target = self.filebrowser

# load prefab
        self.load_prefab_button = load_prefab('editor_button')
        self.load_prefab_button.parent = self.load_menu_parent
        self.load_prefab_button.name = 'load_prefab_button'
        self.load_prefab_button.scale = (.1, .05)
        self.load_prefab_button.text = 'prefab'
        self.menu_toggler = self.load_prefab_button.add_script('menu_toggler')
        self.load_prefab_button.add_script('open_in_file_explorer')
        self.load_prefab_button.open_in_file_explorer.path = Filename.toOsSpecific(application.prefab_folder)

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.parent = self
        self.filebrowser.position = (0,0)
        self.filebrowser.enabled = False
        self.filebrowser.file_types = ('.py')
        self.filebrowser.path = application.prefab_folder
        self.filebrowser.button_type = 'load_prefab_button'
        self.menu_toggler.target = self.filebrowser


# load model
        self.load_model_button = load_prefab('editor_button')
        self.load_model_button.parent = self.load_menu_parent
        self.load_model_button.name = 'load_model_button'
        self.load_model_button.scale = (.1, .05)
        self.load_model_button.text = 'model'
        self.menu_toggler = self.load_model_button.add_script('menu_toggler')
        self.load_model_button.add_script('open_in_file_explorer')
        self.load_model_button.open_in_file_explorer.path = Filename.toOsSpecific(application.model_folder)

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.file_types = ('.egg')
        self.filebrowser.path = application.model_folder
        self.filebrowser.button_type = 'load_model_button'
        self.menu_toggler.target = self.filebrowser

# load primitive
        self.load_primitive_button = load_prefab('editor_button')
        self.load_primitive_button.parent = self.load_menu_parent
        self.load_primitive_button.name = 'load_primitive_button'
        self.load_primitive_button.scale = (.1, .05)
        self.load_primitive_button.text = 'primitive'
        self.menu_toggler = self.load_primitive_button.add_script('menu_toggler')
        self.load_primitive_button.add_script('open_in_file_explorer')
        self.load_primitive_button.open_in_file_explorer.path = Filename.toOsSpecific(application.internal_model_folder)

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.file_types = ('.egg')
        self.filebrowser.path = application.internal_model_folder
        self.filebrowser.button_type = 'load_model_button'
        self.menu_toggler.target = self.filebrowser

# load sprites
        self.load_sprite_button = load_prefab('editor_button')
        self.load_sprite_button.parent = self.load_menu_parent
        self.load_sprite_button.name = 'load_sprite_button'
        self.load_sprite_button.scale = (.1, .05)
        self.load_sprite_button.text = 'sprite'
        self.menu_toggler = self.load_sprite_button.add_script('menu_toggler')
        self.load_sprite_button.add_script('open_in_file_explorer')
        self.load_sprite_button.open_in_file_explorer.path = Filename.toOsSpecific(application.compressed_texture_folder)

        self.filebrowser = load_prefab('filebrowser')
        self.filebrowser.file_types = ('.png', '.jpg', '.gif')
        self.filebrowser.path = application.compressed_texture_folder
        self.filebrowser.button_type = 'load_texture_button'
        self.menu_toggler.target = self.filebrowser

        self.layout_group.update_grid()


# entity list
        self.entity_list = load_prefab('entity_list')
        self.entity_list.parent = self
        self.entity_list.populate()

        self.entity_list_header = load_prefab('editor_button')
        self.entity_list_header.parent = self
        self.entity_list_header.z = -2
        self.entity_list_header.color = (color.lime + color.black) / 2
        self.entity_list_header.position = window.top_left
        self.entity_list_header.origin = (-.5, .5)
        self.entity_list_header.scale = (.25, .025)
        self.entity_list_header.text = scene.entity.name
        self.entity_list_header.text_entity.align = 'left'
        self.entity_list_header.text_entity.x = -.45
        self.entity_list_header.add_script('menu_toggler')
        self.entity_list_header.menu_toggler.target = self.entity_list

        self.save_scene_button = load_prefab('editor_button')
        self.save_scene_button.parent = self.entity_list_header
        self.save_scene_button.color = color.green
        self.save_scene_button.text = 's'
        self.save_scene_button.origin = (0.5, 0)
        self.save_scene_button.position = (1, -.5, -3)
        self.save_scene_button.scale_x = .15
        self.save_scene_button.add_script('save_scene_button')

        # self.ask_for_scene_name_menu = load_prefab('ask_for_scene_name_menu')


        # self.save_scene_button.input = MethodType(self.input, self.save_scene_button)
        # self.save_scene_button.input(self, 't')

        # self.entity_search = load_prefab('editor_button')
        # self.entity_search.parent = self
        # self.entity_search.color = (color.lime + color.black) / 2
        # self.entity_search.position = window.top_left
        # self.entity_search.y -= .025
        # self.entity_search.z = -2
        # self.entity_search.origin = (-.5, .5)
        # self.entity_search.scale = (.2, .025)
        # self.entity_search.text = 'search:'
        # self.entity_search.text_entity.origin = (-.5,0)
        # self.entity_search.text_entity.x = -.45

# inspector
        self.inspector = load_prefab('inspector')
        self.inspector.parent = self

# view front
        self.toggle_button = load_prefab('editor_button')
        self.toggle_button.is_editor = True
        self.toggle_button.parent = self
        self.toggle_button.name = 'toggle_button'
        self.toggle_button.origin = (0, .5)
        self.toggle_button.position = window.top_right
        self.toggle_button.x -= .1
        self.toggle_button.scale = (.1, .05)
        self.toggle_button.text = 'front'
        self.toggle_button.add_script('toggle_sideview')

# exit button
        self.exit_button = load_prefab('editor_button')
        self.exit_button.is_editor = True
        self.exit_button.parent = self
        self.exit_button.name = 'toggle_button'
        self.exit_button.origin = (.5, .5)
        self.exit_button.position = window.top_right
        self.exit_button.scale = (.06, .03)
        self.exit_button.text = 'X'
        self.exit_button.text_entity.x = 0
        # self.exit_button.add_script('toggle_sideview')

        # from panda3d.core import DirectionalLight
        # from panda3d.core import VBase4
        # light = DirectionalLight('light')
        # light.setColor(VBase4(1, 1, 1, 1))
        # dlnp = render.attachNewNode(light)
        # dlnp.setHpr(0, -60, 60)
        # # dlnp.setPos(0, -10, 10)
        # dlnp.setPos(0, 0, 32)
        # dlnp.setScale(100)
        # # dlnp.lookAt(0, 0, 0)
        # dlnp.node().getLens().setNearFar(.2, 100)
        # # dlnp.node().getLens().setFocalLength(100)
        #
        # render.setLight(dlnp)
        # # Use a 512x512 resolution shadow map
        # light.setShadowCaster(True, 2048, 2048)
        # # Enable the shader generator for the receiving nodes
        # # render.setShaderAuto()
        # light.showFrustum()

        # ground = Entity()
        # ground.model = 'quad'
        # ground.y = .1
        # ground.rotation_x = -90
        # ground.scale *= 10
        # ground.setShaderAuto()

        # cube = Entity()
        # cube.model = 'cube'
        # cube.origin = (0, -.5, 0)
        # cube.setShaderAuto()

        # self.t = load_prefab('text')
        # self.t.text = 'test text'

        # self.text.color = color.smoke
        # self.text.parent = scene.ui



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
        #         c.color = color.color(x * 30, 1, (z + 1) / 10)
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


#         self.text_editor = Entity()
#         self.text_editor.parent = self
#         self.text_bg = load_prefab('editor_button')
#         self.text_bg.parent = self.text_editor
#         self.text_bg.scale = (.6, .8)
#         self.text_bg.button_script._highlight_color = self.text_bg.button_script.color
#
#         # text = ''
#         # for i in range(70):
#         #     text += str('1')
#         text ='''import sys
# sys.path.append("..")
# from pandaeditor import *
# import os
# from panda3d.bullet import BulletDebugNode
# from types import MethodType
#
# class Editor(Entity):
#
#     def input(self, key):
#         print('2')
#
#     def __init__(self):
#         super().__init__()
#         self.name = 'editor'
#         self.is_editor = True
#         self.parent = scene.ui
#                 '''
#         self.text_bg.text = text
#         self.text_bg.text_entity.align = 'left'
#         # self.text_editor.text_entity.origin = (-.5, .5)
#         self.text_bg.text_entity.position = (-.45, .45)

        # self.compress_textures()
        # self.compress_models()

        # player = load_prefab('first_person_controller', True)
        # voxel_tool = load_prefab('voxel_tool', True)

    def update(self, dt):
        self.editor_camera_script.update(dt)
        self.transform_gizmo.update(dt)
        # self.inspector.update(dt)

    def input(self, key):
        # if key == 'l':
        #     render.setShaderAuto()
        #     print('set shader auto')

        if held_keys['control'] and key == 'z':
            undo.stack().undo()
        if held_keys['control'] and key == 'y':
            undo.stack().redo()

        if key == 'c':
            # print('show colliders')
            for e in scene.entities:
                if not e.is_editor and e.editor_collider:
                    e.editor_collider.node_path.show()

        if key == 'c up':
            # print('hide colliders')
            for e in scene.entities:
                if not e.is_editor and e.editor_collider:
                    e.editor_collider.node_path.hide()

        if key == 'n':
            scene.new()
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

        if self.enabled:
            self.editor_camera_script.input(key)


    def on_disable(self):
        self.transform_gizmo.enabled = False
        self.grid.enabled = False
        # disable editor
        self.editor_camera_script.position = camera.position
        camera.wrtReparentTo(scene.render)
        for e in scene.entities:
            if e.is_editor:
                continue
            try:
                e.editor_collider.stash()
                e.collider.unstash()
            except:
                pass
            # try:
            #     e.start()
            # except:
            #     pass
            for s in e.scripts:
                try:
                    s.start()
                except:
                    pass


    def on_enable(self):
        # enable editor
        # if self.enabled:
        camera.wrtReparentTo(self.camera_pivot)
        camera.position = self.editor_camera_script.position

        for e in scene.entities:
            if e.is_editor or e is scene.entity:
                continue

            try:
                e.editor_collider = 'box'
                e.collider.stash()
            except:
                pass
            try:
                e.stop()
            except:
                pass
            for s in e.scripts:
                try:
                    s.stop()
                except:
                    pass
        self.transform_gizmo.enabled = True
        self.grid.enabled = True
        mouse.locked = False


    def compress_textures(self):
        from PIL import Image
        from os.path import dirname
        files = os.listdir(application.texture_folder)
        compressed_files = os.listdir(application.compressed_texture_folder)
        # print(files)
        texture_dir = os.path.join(
            dirname(dirname(dirname(os.path.abspath(__file__)))),
            'textures'
            )

        for f in files:
            if f.endswith('.psd') or f.endswith('.png'):
                print('f:', application.compressed_texture_folder + '/' + f)

                image = Image.open(os.path.join(texture_dir, f))
                # print(max(image.size))
                if max(image.size) > 256:
                    image.save(
                        os.path.join(texture_dir, 'compressed', f[:-4] + '.jpg'),
                        'JPEG',
                        quality=80,
                        optimize=True,
                        progressive=True
                        )
                    print('compressing to jpg:', f)
                else:
                    image.save(
                        os.path.join(texture_dir, 'compressed', f[:-4] + '.png'),
                        'PNG'
                        )
                    print('compressing to png:', f)
            # elif f.endswith('.png'):

    def compress_models(self):
        import subprocess
        subprocess.call(r'''"C:\Program Files\Blender Foundation\Blender\blender.exe" "D:\UnityProjects\pandagame\pandaeditor\internal_models\cube.blend" --background --python "D:\UnityProjects\pandagame\pandaeditor\internal_scripts\blend_export.py"''')
        return
        from tinyblend import BlenderFile
        from os.path import dirname
        files = os.listdir(application.model_folder)
        compressed_files = os.listdir(application.compressed_model_folder)
        # print(files)
        texture_dir = os.path.join(
            dirname(dirname(dirname(os.path.abspath(__file__)))),
            'textures'
            )

        for f in files:
            if f.endswith('.blend'):
                # print('f:', application.compressed_model_folder + '/' + f)
                print('______', f)
                blend = BlenderFile(application.model_folder + '/' + f)
                # objects = blend.list('Object')
                for o in blend.list('Object'):
                    # print(o.id.name.decode("utf-8", "strict"))
                    object_name = o.id.name.decode( "utf-8").replace(".", "_")[2:]
                    object_name = object_name.split('\0', 1)[0]
                    print('name:', object_name)
                    file_name = ''.join([f.split('.')[0], '_', object_name, '.egg'])
                    file_path = os.path.join(
                        str(Filename.toOsSpecific(application.compressed_model_folder)),
                        file_name
                    )
                    print(file_path)
                    print(len(o.data.mloop))

                    # for v in o.data.mvert:
                    #     print('vertex:', v.co)
                    # for e in o.data.medge:
                    #     print('edge:', e.v1, e.v2)
                    # for i in range(0, len(o.data.mloop), 3):
                    #     print('triangle:',
                    #         o.data.mloop[i].v,
                    #         o.data.mloop[i+1].v,
                    #         o.data.mloop[i+2].v
                    #     )
                    with open(file_path, 'w') as file:
                        file.write(
                            '<CoordinateSystem> { Z-up }\n'
                            + '<Group> ' + object_name + ' {\n'
                            +
'''<Transform> {
    <Matrix4> {
      1.0 0.0 0.0 0.0
      0.0 1.0 0.0 0.0
      0.0 0.0 1.0 0.0
      0.0 0.0 0.0 1.0
    }
  }'''

                            + '  <VertexPool> ' + object_name + ' {\n'
                        )
                        for i in range(len(o.data.mvert)):
                            file.write(
                                '    <Vertex> '
                                + str(i)
                                + ' {' + str(o.data.mvert[i].co[0])
                                + ' ' + str(o.data.mvert[i].co[1])
                                + ' ' + str(o.data.mvert[i].co[2]) + '\n'
                                + '      <UV> ORCO {' + '\n'
                                + '        ' + '0.000000 0.000000' + '\n'
                                + '      }\n'
                                + '    }\n'
                            )
                        file.write('  }\n')

                        for i in range(0, len(o.data.mloop)-2, 3):
                            file.write(''.join([
                                '  <Polygon> {\n',
                                '    <Normal> {', '0 0 0',  '}\n',
                                '    <VertexRef> { ',
                                str(o.data.mloop[i].v), ' ',
                                str(o.data.mloop[i+1].v), ' ',
                                str(o.data.mloop[i+2].v), ' <Ref> { ',
                                object_name, ' }}\n',
                                '  }\n'
                            ])
                            )

                        file.write('}')
