from ursina import *; unlit_shader = Shader(language=Shader.GLSL, vertex = '''#version 150


uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 texcoords;

void main() {
    gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
    texcoords = p3d_MultiTexCoord0;
}
''',

fragment='''
#version 140

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 texcoords;
out vec4 fragColor;


void main() {
    vec4 color = texture(p3d_Texture0, texcoords) * p3d_ColorScale;
    fragColor = color.rgba;
}

''',
)



if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina()
    window.color=color.black
    # from ursina.lights import DirectionalLight
    # DirectionalLight()



    shader = unlit_shader

    a = AzureCube(shader=shader)
    b = YellowSphere(shader=shader, rotation_y=180, x=3, texture='shore')
    # from panda3d.core import Material
    # myMaterial = Material()
    # myMaterial.setShininess(5.0) #Make this material shiny
    # myMaterial.setAmbient((0, 0, 1, 1)) #Make this material blue
    # b.set_material(myMaterial)
    # AzureSphere(shader=a.shader, y=2)
    GrayPlane(scale=10, y=-2, texture='shore', shader=shader)

    from panda3d.core import *
    # Add a sun source.
    sun = DirectionalLight("sun")
    # sun.set_color_temperature(6000)
    sun.color = color.white
    sun_path = render.attach_new_node(sun)
    sun_path.set_pos(10, 10, -10)
    sun_path.look_at(0, 0, 0)
    # sun_path.hprInterval(10.0, (sun_path.get_h(), sun_path.get_p() - 360, sun_path.get_r()), bakeInStart=True).loop()
    render.set_light(sun_path)

    # Enable shadows; we need to set a frustum for that.
    sun.get_lens().set_near_far(1, 30)
    sun.get_lens().set_film_size(20, 40)
    # sun.show_frustum()
    sun.set_shadow_caster(True, 1024, 1024)

    bmin, bmax = scene.get_tight_bounds(sun_path)
    lens = sun.get_lens()
    lens.set_film_offset((bmin.xy + bmax.xy) * 0.5)
    lens.set_film_size(bmax.xy - bmin.xy)
    lens.set_near_far(bmin.z, bmax.z)

    Sky(color=color.light_gray)
    EditorCamera()

    app.run()
