from ursina import *

from ursina.shaders.triplanar_shader import triplanar_shader

app = Ursina()


from ursina.editor.level_editor import level_editor, Scene, goto_scene
goto_scene(0,0)

e = Entity(model='cube', scale=(10,2,10), y=-1, shader=triplanar_shader, texture='brick', selectable=True, collider='box', original_parent=scene)
e.set_shader_input('top_texture', load_texture('grass', path=application.internal_textures_folder))
level_editor.entities.append(e)

e = Entity(model='cube', scale=(2,2,2), y=1, shader=triplanar_shader, texture='brick', selectable=True, collider='box', original_parent=scene)
e.set_shader_input('top_texture', load_texture('grass', path=application.internal_textures_folder))
level_editor.entities.append(e)


app.run()
