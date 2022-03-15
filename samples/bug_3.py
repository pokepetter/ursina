from ursina import *


app = Ursina()

#
# application.asset_folder = Path(r'''D:\3d''')
#
# # from ursina.shaders.triplanar_shader import triplanar_shader
# # from ursina.shaders.lit_with_shadows_shader import lit_with_shadows_shader
#
# # m = load_model('metarock_test.bam')
# # if not m:
# #     m = load_model('metarock_test.obj', path=Path(r'''D:\3d'''), use_deepcopy=True)
# #     m.generate_normals()
# #     m.save('metarock_test.bam')
# #
# # e = Entity(model=m, shader=lit_with_shadows_shader, texture='dirt', scale=.1, collider=load_model('metarock_test_collider.obj', path=Path(r'''D:\3d''')))
# e = Entity(model='metarock_test_2', texture='metarock_test.jpg', scale=.1, collider=load_model('metarock_test_collider.obj', path=Path(r'''D:\3d''')))
#
# Sky()
EditorCamera()
# # from ursina.prefabs.first_person_controller import FirstPersonController
# # player = FirstPersonController(y=2)
# camera.fov = 90
# # DirectionalLight()

start_point = Entity(model='sphere', color=color.orange, scale=.25, position=(-2,-1))
end_point = Entity(model='sphere', color=color.orange, scale=.25, position=(2,1))

line = Entity(model='line', origin_x=-.5, position=start_point.world_position, scale_x=distance_2d(start_point, end_point))
line.look_at_2d(end_point)
# line = Entity(model='cube', origin_z=-.5, position=start_point.world_position, scale_z=distance(start_point, end_point))
# line.look_at(end_point, axis='')

app.run()
