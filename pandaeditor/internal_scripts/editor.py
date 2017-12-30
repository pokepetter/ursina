import os
from panda3d.bullet import BulletDebugNode
from types import MethodType
# import debugwindow

from pandaeditor import *
from pandaeditor.internal_prefabs.transform_gizmo import TransformGizmo
from pandaeditor.internal_prefabs.entity_list import EntityList
from pandaeditor.internal_prefabs.inspector import Inspector
from pandaeditor.internal_scripts.editor_camera import EditorCamera




class Editor(Entity):

    def __init__(self):
        super().__init__()
        self.name = 'editor'
        self.is_editor = True
        self.parent = scene.ui

        self.trash = NodePath('trash')
        self.selection = list()

        self.editor_camera = EditorCamera()


        self.transform_gizmo = TransformGizmo()
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
        self.play_button = EditorButton()
        self.play_button.parent = self.top_menu
        self.play_button.origin = (0, .5)
        self.play_button.name = 'play_button'
        self.play_button.scale = (.1, .05)
        self.play_button.text = 'play'
        # self.menu_toggler = self.play_button.add_script('menu_toggler')

        self.pause_button = EditorButton()
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
        self.load_menu_parent.position = window.right
        self.load_menu_parent.y -= .1
        self.layout_group = self.load_menu_parent.add_script('grid_layout')
        self.layout_group.origin = (.5, .5)
        self.layout_group.max_x = 1
        self.layout_group.spacing = (0, .001)

        button_names = ('scenes', 'prefabs', 'models', 'primitives', 'sprites')
        button_paths = (
            application.scene_folder,
            application.prefab_folder,
            application.model_folder,
            application.internal_model_folder,
            application.texture_folder
            )
        file_types = (('.py'), ('.py'), ('.egg'), ('.egg'), ('.png', '.jpg', '.gif'))
        button_types = (
            'load_scene_button',
            'load_prefab_button',
            'load_model_button',
            'load_primitive_button',
            'load_sprite_button'
            )

        for i in range(len(button_names)):
            try:
                b = EditorButton()
                b.parent = self.load_menu_parent
                b.name = button_names[i]
                b.origin = (.5, 0)
                b.scale = (.1, .05)
                b.text = button_names[i]
                menu_toggler = b.add_script('menu_toggler')
                b.add_script('open_in_file_explorer')
                b.open_in_file_explorer.path = button_paths[i]
                print('_______', b.name, 'path:', b.open_in_file_explorer.path)

                filebrowser = Filebrowser()
                filebrowser.parent = self
                filebrowser.enabled = False
                filebrowser.file_types = file_types[i]
                filebrowser.path = button_paths[i]
                filebrowser.button_type = button_types[i]
                menu_toggler.target = filebrowser
            except Exception as e:
                print(e)


        self.layout_group.update_grid()


# entity list
        self.entity_list = EntityList()
        self.entity_list.parent = self
        self.entity_list.populate()

        self.entity_list_header = EditorButton()
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

        self.save_scene_button = EditorButton()
        self.save_scene_button.parent = self.entity_list_header
        self.save_scene_button.color = color.green
        self.save_scene_button.text = 's'
        self.save_scene_button.origin = (0.5, 0)
        self.save_scene_button.position = (1, -.5, -3)
        self.save_scene_button.scale_x = .15
        self.save_scene_button.add_script('save_scene_button')


# inspector
        self.inspector = Inspector()
        self.inspector.parent = self

# view front
        self.toggle_button = EditorButton()
        self.toggle_button.is_editor = True
        self.toggle_button.parent = self
        self.toggle_button.name = 'toggle_button'
        self.toggle_button.origin = (0, .5)
        self.toggle_button.position = window.top_right
        self.toggle_button.x -= .1
        self.toggle_button.scale = (.1, .05)
        self.toggle_button.text = 'front'
        self.toggle_button.add_script('toggle_sideview')



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

        # self.t = Text()
        # self.t.text = 'test text'

        # self.text.color = color.smoke
        # self.text.parent = scene.ui


#         self.text_editor = Entity()
#         self.text_editor.parent = self
#         self.text_bg = EditorButton()
#         self.text_bg.parent = self.text_editor
#         self.text_bg.scale = (.6, .8)
#         self.text_bg.button_script._highlight_color = self.text_bg.button_script.color
#

        # self.compress_textures()
        # self.compress_models()
        scene.sky.color = color.gray


    def update(self, dt):
        self.transform_gizmo.update(dt)

    def input(self, key):
        # if key == 'l':
        #     render.setShaderAuto()
        #     print('set shader auto')

        if held_keys['control'] and key == 'z':
            undo.stack().undo()
        if held_keys['control'] and key == 'y':
            undo.stack().redo()


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

        # if self.enabled:
        #     self.editor_camera_script.input(key)



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


if __name__ == '__main__':
    app = main.PandaEditor()
    scene.editor = Editor()
    app.run()
