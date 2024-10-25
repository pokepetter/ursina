from ursina import Shader, color; blood_shader = Shader(name='blood_shader', language=Shader.GLSL, vertex='''#version 130
uniform mat4 p3d_ModelViewProjectionMatrix;

in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;

out vec2 texcoord;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoord = p3d_MultiTexCoord0;
}

''',
fragment='''
#version 130

uniform sampler2D p3d_Texture0;
uniform sampler2D noise_texture;
uniform float blood_coef;
uniform float surface_opacity_influence;
uniform vec3 blood_color;

in vec2 texcoord;
out vec4 fragColor;

void main() {
    vec4 surface_texture = texture(p3d_Texture0, texcoord);
    vec4 noise_tex_sample = texture(noise_texture, texcoord);

    float blood_opacity = mix(1.0, surface_texture.a, surface_opacity_influence);
    vec4 final_blood_color = vec4(noise_tex_sample.rgb * blood_color, blood_opacity);

    float is_blood = step(noise_tex_sample.r, blood_coef);
    fragColor = mix(surface_texture, final_blood_color, is_blood);
}

''',
default_input={
    'blood_coef': .5,
    'blood_color': color.red,
    'surface_opacity_influence': 1.0 # the opacity of the surface texture influences the opacity of the blood [0.0; 1.0]
    }
)


if __name__ == '__main__':
    from ursina import *

    app = Ursina()

    Entity(model='plane', texture='grass', scale=16)
    sphere = Entity(model='sphere', texture='shore', y=2, shader=blood_shader)
    sphere.set_shader_input('noise_texture', load_texture("perlin_noise.png")) # default ursina noise texture

    blood_anim = Entity(blood_amount = 0)
    blood_anim.animate(name='blood_amount', value=.5, duration=4, curve=curve.linear_boomerang, loop=True)
    def update():
        sphere.set_shader_input('blood_coef', blood_anim.blood_amount)

    Sky(color=color.light_gray)
    EditorCamera()

    app.run()
