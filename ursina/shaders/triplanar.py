from ursina import *


triplanar_shader = Shader(
vertex='''
#version 140
uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 transform_matrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
in vec3 p3d_Normal;
out vec2 texcoord;
out vec3 world_space_normal;
out vec3 vertex_position;


void main() {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
  texcoord = p3d_MultiTexCoord0;

  world_space_normal = normalize(transpose( inverse(mat3(transform_matrix)) ) * p3d_Normal.xyz);
  vertex_position = p3d_Vertex.xyz;
}
''',

fragment='''
#version 140

uniform vec4 p3d_ColorScale;
in vec2 texcoord;
out vec4 fragColor;

uniform sampler2D p3d_Texture0;
uniform sampler2D top_texture;
in vec3 world_space_normal;
in vec3 vertex_position;

in vec2 normalRepeat;
in vec2 normalScale;

//"Standard" triplanar blending.
vec3 TriPlanarBlendWeightsStandard(vec3 normal) {
	vec3 blend_weights = abs(normal.xyz);

    float blendZone = 0.55;//anything over 1/sqrt(3) or .577 will produce negative values in corner
	blend_weights = blend_weights - blendZone;

	blend_weights = max(blend_weights, 0.0);
	float rcpBlend = 1.0 / (blend_weights.x + blend_weights.y + blend_weights.z);
	return blend_weights*rcpBlend;
}

//Constant width Triplanar blending
vec3 TriPlanarBlendWeightsConstantOverlap(vec3 normal) {

	vec3 blend_weights = normal*normal;//or abs(normal) for linear falloff(and adjust BlendZone)
	float maxBlend = max(blend_weights.x, max(blend_weights.y, blend_weights.z));

    float BlendZone = 0.8f;
	blend_weights = blend_weights - maxBlend*BlendZone;

	blend_weights = max(blend_weights, 0.0);

	float rcpBlend = 1.0 / (blend_weights.x + blend_weights.y + blend_weights.z);
	return blend_weights*rcpBlend;
}

void main(){
    // vec3 world_space_normal = vec3(world_space_normal.x, world_space_normal.z, world_space_normal.y);
    // vec3 vertex_position = vec3(vertex_position.x, vertex_position.z, vertex_position.y);
    vec3 blendFast = TriPlanarBlendWeightsConstantOverlap(world_space_normal);
    vec3 blend = blendFast;

    vec3 albedoX = texture(p3d_Texture0, vertex_position.yz).rgb*blend.x;
	vec3 albedoY = texture(p3d_Texture0, vertex_position.xz).rgb*blend.y;
	vec3 albedoZ = texture(p3d_Texture0, vertex_position.xy).rgb*blend.z;

    if (world_space_normal.z > .0) {
		albedoZ = texture(top_texture, vertex_position.xy).rgb*blend.z;
    }

	vec3 triPlanar = (albedoX + albedoY + albedoZ);

    fragColor = vec4(triPlanar.rgb, 1);
}

''',
geometry='',
default_input = {
    'transform_matrix' : Mat4(),
    'normalRepeat' : Vec2(10,10),
    'normalScale' : Vec2(1,1),
    'top_texture' : None
    }
)


if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina()
    window.color=color.black

    # e = Entity(model='sphere', texture='brick', shader=empty_shader)
    # e.setShaderInput('transform_matrix', e.getNetTransform().getMat())
    shader = triplanar_shader

    a = WhiteCube(shader=shader, texture=load_texture('brick'))
    a.model.uvs= []
    a.model.generate()
    # a.model.setTexture(a.texture._texture, 1)
    t = load_texture('brick')._texture
    print('------', type(t))
    a.set_shader_input('top_texture', load_texture('shore')._texture)
    # print('---------', a.texture._texture)

    b = AzureSphere(shader=shader, rotation_y=180, x=3, texture='brick')
    b.texture.filtering = False
    GrayPlane(scale=10, y=-2, texture='shore')
    b.set_shader_input('top_texture', load_texture('shore')._texture)

    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        b.rotation_y += 1
        b.rotation_x += 1
        b.set_shader_input('transform_matrix', b.getNetTransform().getMat())

    app.run()
