from ursina import color
from ursina.shader import Shader
from ursina.vec2 import Vec2
from ursina.vec3 import Vec3

triplanar_shader = Shader(
name='triplanar_shader', language=Shader.GLSL,
vertex='''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelMatrix;
in vec2 p3d_MultiTexCoord0;
in vec4 p3d_Vertex;
in vec3 p3d_Normal;
in vec4 p3d_Color;
out vec3 world_normal;
out vec3 vertex_world_position;
out vec2 texcoord;
out vec4 vertex_color;

void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texcoord = p3d_MultiTexCoord0;

  world_normal = normalize(mat3(p3d_ModelMatrix) * p3d_Normal);
  vertex_world_position = (p3d_ModelMatrix * p3d_Vertex).xyz;
  vertex_color = p3d_Color;
}
''',

fragment='''
#version 140

uniform vec4 p3d_ColorScale;
in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D p3d_Texture0;
uniform sampler2D side_texture;
in vec3 world_normal;
in vec3 vertex_world_position;

uniform vec2 texture_scale;
uniform vec2 side_texture_scale;

in vec4 vertex_color;


//"Standard" triplanar blending.
vec3 TriPlanarBlendWeightsStandard(vec3 normal) {
	vec3 blend_weights = abs(normal.xyz);

    float blendZone = 0.55;//anything over 1/sqrt(3) or .577 will produce negative values in corner
	blend_weights = blend_weights - blendZone;

	blend_weights = max(blend_weights, 0.0);
	float rcpBlend = 1.0 / (blend_weights.x + blend_weights.y + blend_weights.z);
	return blend_weights*rcpBlend;
}

void main() {
    // vec3 blendFast = TriPlanarBlendWeightsConstantOverlap(world_normal);

    //Constant width Triplanar blending
    vec3 blend_weights = world_normal * world_normal;//or abs(world_normal) for linear falloff(and adjust BlendZone)
    float maxBlend = max(blend_weights.x, max(blend_weights.y, blend_weights.z));

    float BlendZone = 0.8f;
    blend_weights = blend_weights - maxBlend*BlendZone;
    blend_weights = max(blend_weights, 0.0);

    float rcpBlend = 1.0 / (blend_weights.x + blend_weights.y + blend_weights.z);
    vec3 blend = blend_weights * rcpBlend;

    vec3 albedoX = texture(side_texture, vertex_world_position.zy * side_texture_scale).rgb*blend.x;
    vec3 albedoY = texture(side_texture, vertex_world_position.xz * side_texture_scale).rgb*blend.y;
    vec3 albedoZ = texture(side_texture, vertex_world_position.xy * side_texture_scale).rgb*blend.z;

    if (world_normal.y > .0) {
        albedoY = texture(p3d_Texture0, vertex_world_position.xz * texture_scale.xy).rgb*blend.y;
    }

    vec3 triPlanar = (albedoX + albedoY + albedoZ);

    fragColor = vec4(triPlanar.rgba) * vertex_color;
}

''',
geometry='',
default_input = {
    'texture_scale' : Vec2(1,1),
    'side_texture' : 'brick',
    'side_texture_scale' : Vec2(1,1),
    }
)


if __name__ == '__main__':
    from ursina import Draggable, EditorCamera, Entity, Sky, Slider, Ursina, color, load_texture, scene, window
    app = Ursina()
    window.color=color.black

    # e = Entity(model='sphere', texture='brick', shader=empty_shader)
    # e.setShaderInput('transform_matrix', e.getNetTransform().getMat())
    shader = triplanar_shader

    a = Draggable(parent=scene, model='cube', shader=shader, texture=load_texture('brick'), plane_direction=Vec3(0,1,0))
    # a.model.uvs= []
    # a.model.generate()
    # a.model.setTexture(a.texture._texture, 1)
    t = load_texture('brick')._texture
    print('------', type(t))
    a.set_shader_input('side_texture', load_texture('brick'))
    # print('---------', a.texture._texture)

    b = Entity(model='sphere', shader=shader, color=color.azure, rotation_y=180, x=3, texture='grass')
    b.texture.filtering = False
    Entity(model='plane', color=color.gray, scale=10, y=-2, texture='shore')
    b.set_shader_input('side_texture', load_texture('brick'))

    Sky(color=color.light_gray)
    EditorCamera()

    def set_side_texture_scale():
        value = side_texture_scale_slider.value
        b.set_shader_input('side_texture_scale', Vec2(value, value))
        a.set_shader_input('side_texture_scale', Vec2(value, value))

    side_texture_scale_slider = Slider(text='side_texture_scale', min=0, max=10, default=1, dynamic=True, on_value_changed=set_side_texture_scale)


    def update():
        b.rotation_y += 1
        b.rotation_x += 1

    app.run()
