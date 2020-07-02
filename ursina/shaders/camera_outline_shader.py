from ursina import *

empty_shader = Shader(
vertex='''
#version 130
// Exactly nothing happens in vertex shading.

in vec4 p3d_Vertex;
uniform mat4 p3d_ModelViewProjectionMatrix;

void main()  {
  gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
}
''',

fragment='''
#version 130
uniform sampler2D tex;
uniform sampler2D dtex;
out vec4 color;

void main () {
  vec4 color_base = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2(0, 0), 0);
  vec4 color_1 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2(-1, -1), 0);
  vec4 color_2 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2(-1,  0), 0);
  vec4 color_3 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2(-1,  1), 0);
  vec4 color_4 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 0, -1), 0);
  vec4 color_5 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 0,  1), 0);
  vec4 color_6 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 1, -1), 0);
  vec4 color_7 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 1,  0), 0);
  vec4 color_8 = texelFetch(dtex, ivec2(gl_FragCoord.xy) + ivec2( 1,  1), 0);
  color = (abs(color_base - color_1) +
           abs(color_base - color_2) +
           abs(color_base - color_3) +
           abs(color_base - color_4) +
           abs(color_base - color_5) +
           abs(color_base - color_6) +
           abs(color_base - color_7) +
           abs(color_base - color_8)) * vec4(512, 512, 512, 0);
}
'''
,
geometry='')


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    Entity(model='cube', texture='white_cube', color=color.red)
    Entity(model='cube', texture='white_cube', color=color.white, x=1.1)
    Entity(model='sphere', texture='white_cube', color=color.gray, y=1.1)
    # e = Entity(model='quad', scale=3, shader=empty_shader)
    camera.shader = empty_shader
    print(camera.shader)

    t = 0
    frame = 0

    #e.set_shader_input('iResolution', window.size)
    #e.set_shader_input('iTime', t)
    #e.set_shader_input('iFrame', frame)

    def update():
      global t, frame
      t += time.dt
      #e.set_shader_input('iTime', t)

      frame += 1
      #e.set_shader_input('iFrame', frame)


    EditorCamera()

    app.run()
