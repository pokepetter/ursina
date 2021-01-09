from ursina import *

fxaa_shader = Shader(language=Shader.GLSL,
fragment='''
//fragment shader, the interesting part!
#version 400
uniform sampler2D tex;  //the rendered framebuffer containing the color bound as sampler2D
uniform vec2 window_size;    //the size of the window/framebuffer

in vec2 uv;

layout( location = 0 ) out vec4 color; //the manipulated color output

//////////////////////////////////////////////////////////////////////////////
//FXAA
#ifndef FXAA_REDUCE_MIN
    #define FXAA_REDUCE_MIN   (1.0/ 128.0)
#endif
#ifndef FXAA_REDUCE_MUL
    #define FXAA_REDUCE_MUL   (1.0 / 8.0)
#endif
#ifndef FXAA_SPAN_MAX
    #define FXAA_SPAN_MAX     8.0
#endif

//optimized version for mobile, where dependent
//texture reads can be a bottleneck
vec4 fxaa(sampler2D tex, vec2 fragCoord, vec2 resolution) {
    vec4 color;

  vec2 inverseVP = 1.0 / resolution.xy;

  vec2 v_rgbNW = (fragCoord + vec2(-1.0, -1.0)) * inverseVP;
  vec2 v_rgbNE = (fragCoord + vec2(1.0, -1.0)) * inverseVP;
  vec2 v_rgbSW = (fragCoord + vec2(-1.0, 1.0)) * inverseVP;
  vec2 v_rgbSE = (fragCoord + vec2(1.0, 1.0)) * inverseVP;
  vec2 v_rgbM = vec2(fragCoord * inverseVP);

  vec3 rgbNW = texture2D(tex, v_rgbNW).xyz;
  vec3 rgbNE = texture2D(tex, v_rgbNE).xyz;
  vec3 rgbSW = texture2D(tex, v_rgbSW).xyz;
  vec3 rgbSE = texture2D(tex, v_rgbSE).xyz;
  vec4 texColor = texture2D(tex, v_rgbM);
  vec3 rgbM  = texColor.xyz;
  vec3 luma = vec3(0.299, 0.587, 0.114);
  float lumaNW = dot(rgbNW, luma);
  float lumaNE = dot(rgbNE, luma);
  float lumaSW = dot(rgbSW, luma);
  float lumaSE = dot(rgbSE, luma);
  float lumaM  = dot(rgbM,  luma);
  float lumaMin = min(lumaM, min(min(lumaNW, lumaNE), min(lumaSW, lumaSE)));
  float lumaMax = max(lumaM, max(max(lumaNW, lumaNE), max(lumaSW, lumaSE)));

  mediump vec2 dir;
  dir.x = -((lumaNW + lumaNE) - (lumaSW + lumaSE));
  dir.y =  ((lumaNW + lumaSW) - (lumaNE + lumaSE));

  float dirReduce = max((lumaNW + lumaNE + lumaSW + lumaSE) *
                        (0.25 * FXAA_REDUCE_MUL), FXAA_REDUCE_MIN);

  float rcpDirMin = 1.0 / (min(abs(dir.x), abs(dir.y)) + dirReduce);
  dir = min(vec2(FXAA_SPAN_MAX, FXAA_SPAN_MAX),
            max(vec2(-FXAA_SPAN_MAX, -FXAA_SPAN_MAX),
            dir * rcpDirMin)) * inverseVP;

  vec3 rgbA = 0.5 * (
      texture2D(tex, fragCoord * inverseVP + dir * (1.0 / 3.0 - 0.5)).xyz +
      texture2D(tex, fragCoord * inverseVP + dir * (2.0 / 3.0 - 0.5)).xyz);
  vec3 rgbB = rgbA * 0.5 + 0.25 * (
      texture2D(tex, fragCoord * inverseVP + dir * -0.5).xyz +
      texture2D(tex, fragCoord * inverseVP + dir * 0.5).xyz);

  float lumaB = dot(rgbB, luma);
  if ((lumaB < lumaMin) || (lumaB > lumaMax))
      color = vec4(rgbA, texColor.a);
  else
      color = vec4(rgbB, texColor.a);
  return color;
}
//FXAA END
//////////////////////////////////////////////////////////////////////////////

void main () {
  //calculate smoothed color by applying fxaa (usually at sharp edges)
  color.rgb = fxaa(tex, gl_FragCoord.st, window_size).rgb;
  float r = mix(0, 1, gl_FragCoord.x/window_size.x);
  // color.rgb = vec3(0,r*.5,0);
  // color.rgb = texture(tex, uv).rgb;
  color.a = 1.0f;
}
''',
default_input={
    'window_size': window.size,
}
)


if __name__ == '__main__':
    app = Ursina()
    window.color=color.black

    # b = Entity(model='sphere')
    Entity(model='plane', scale=10, y=-2, texture='shore')
    # Entity(model='quad', texture='circle', x=2)
    EditorCamera()
    Entity(model='quad', color=color.red, double_sided=True)
    Entity(model='quad', color=color.green, z=-.001, scale=.5, texture='circle')
    # Button(scale=.25, model='circle')
    camera.shader = fxaa_shader
    camera.clip_plane_far=100

    def input(key):
        if key == 'space':
            if not camera.shader:
                camera.shader = fxaa_shader
            else:
                camera.shader = None


    app.run()
