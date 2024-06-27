from ursina import Shader, Vec2, Color; lit_with_shadows_shader = Shader(language=Shader.GLSL, name='lit_with_shadows_shader', vertex = '''#version 150
uniform struct {
    vec4 position;
    vec3 color;
    vec3 attenuation;
    vec3 spotDirection;
    float spotCosCutoff;
    float spotExponent;
    sampler2DShadow shadowMap;
    mat4 shadowViewMatrix;
} p3d_LightSource[1];

const float M_PI = 3.141592653589793;

uniform mat4 p3d_ModelViewProjectionMatrix;
uniform mat4 p3d_ModelViewMatrix;
uniform mat3 p3d_NormalMatrix;

in vec4 vertex;
in vec3 normal;
in vec4 p3d_Color;

in vec2 p3d_MultiTexCoord0;
uniform vec2 texture_scale;
uniform vec2 texture_offset;
out vec2 texcoords;

out vec3 vertex_position;
out vec3 normal_vector;
out vec4 shadow_coord[1];
out vec4 vertex_color;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * vertex;
    vertex_position = vec3(p3d_ModelViewMatrix * vertex);
    normal_vector = normalize(p3d_NormalMatrix * normal);
    shadow_coord[0] = p3d_LightSource[0].shadowViewMatrix * vec4(vertex_position, 1);
    texcoords = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
    vertex_color = p3d_Color;
}

''',
fragment='''
#version 150
uniform struct {
    vec4 position;
    vec3 color;
    vec3 attenuation;
    vec3 spotDirection;
    float spotCosCutoff;
    float spotExponent;
    sampler2DShadow shadowMap;
    mat4 shadowViewMatrix;
} p3d_LightSource[1];

const float M_PI = 3.141592653589793;

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoords;

uniform struct {
    vec4 ambient;
} p3d_LightModel;

uniform struct {
    vec4 ambient;
    vec4 diffuse;
    vec3 specular;
    float roughness;
} p3d_Material;

in vec3 vertex_position;
in vec3 normal_vector;
in vec4 shadow_coord[1];
in vec4 vertex_color;

out vec4 fragment_color;
uniform vec4 shadow_color;

uniform float shadow_blur;
uniform int shadow_samples;

void main() {
    fragment_color = texture(p3d_Texture0, texcoords) * p3d_ColorScale * vertex_color;
    vec3 N = normal_vector;

    float shadow_samples_float = float(shadow_samples);
    float half_shadow_blur = shadow_blur / 2.0;

    for (int i = 0; i < p3d_LightSource.length(); ++i) {
        vec3 diff = p3d_LightSource[i].position.xyz - vertex_position * p3d_LightSource[i].position.w;
        vec3 L = normalize(diff);

        float NdotL = clamp(dot(N, L), 0.001, 1.0);
        vec3 color =  NdotL * p3d_LightSource[i].color / M_PI;
        const float bias = 0.001;

        vec4 shadow_coordinates = shadow_coord[i];
        shadow_coordinates.z += bias;

        vec3 converted_shadow_color = (vec3(1.,1.,1.) - shadow_color.rgb) * shadow_color.a;
        fragment_color.rgb *= p3d_LightSource[i].color.rgb;

        float shadow = 0.0;
        for (int x = 0; x < shadow_samples; ++x) {
            for (int y = 0; y < shadow_samples; ++y) {
                float dx = float(x) * shadow_blur / shadow_samples_float - half_shadow_blur;
                float dy = float(y) * shadow_blur / shadow_samples_float - half_shadow_blur;
                vec4 coord = shadow_coordinates;
                coord.x += dx;
                coord.y += dy;
                shadow += textureProj(p3d_LightSource[i].shadowMap, coord);
            }
        }
        shadow /= (shadow_samples_float * shadow_samples_float);

        fragment_color.rgb += shadow * converted_shadow_color;
        fragment_color.rgb += color - converted_shadow_color;
    }
}

''',
default_input = {
    'texture_scale': Vec2(1,1),
    'texture_offset': Vec2(0,0),
    'shadow_color' : Color(0, .5, 1, .25),
    'shadow_blur': .005,
    'shadow_samples': 4
    }
)


if __name__ == '__main__':
    from ursina import *

    app = Ursina()
    shader = lit_with_shadows_shader

    a = Entity(model='cube', shader=shader, y=1, color=color.light_gray)
    Entity(model='sphere', texture='shore', y=2, x=1, shader=shader)

    Entity(model='plane', scale=16, texture='grass', shader=lit_with_shadows_shader)
    from ursina.lights import DirectionalLight
    sun = DirectionalLight(shadow_map_resolution=(2048,2048))
    sun.look_at(Vec3(-1,-1,-10))
    # sun._light.show_frustum()
    scene.fog_density = (1, 50)
    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        a.x += (held_keys['d'] - held_keys['a']) * time.dt * 5
        a.y += (held_keys['e'] - held_keys['q']) * time.dt * 5
        a.z += (held_keys['w'] - held_keys['s']) * time.dt * 5

    def input(key):
        if key == 'r':
            if sun.color == color.white:
                sun.color = color.red
            else:
                sun.color = color.white

    app.run()
