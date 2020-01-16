from panda3d.core import Shader


camera_contrast_shader = Shader.make('''

void vshader(float4 vtx_position : POSITION,
            float2 vtx_texcoord0 : TEXCOORD0,
            out float4 l_position : POSITION,
            out float2 l_texcoord0 : TEXCOORD0,
            uniform float4 texpad_tex,
            uniform float4x4 mat_modelproj)
{
    l_position=mul(mat_modelproj, vtx_position);
    l_texcoord0 = vtx_position.xz * texpad_tex.xy + texpad_tex.xy;
}

half3 AdjustContrast(half3 color, half contrast) {
    return saturate(lerp(half3(0.5, 0.5, 0.5), color, contrast));
}

void fshader(float2 l_texcoord0 : TEXCOORD0,
             out float4 o_color : COLOR,
             uniform sampler2D k_tex : TEXUNIT0,
             uniform float k_contrast)
{
    float4 c = tex2D(k_tex, l_texcoord0);
    half3 d = half3(c);
    // To have a useless filter that outputs the original view
    // without changing anything, just use :
    //o_color  = c;
    d = AdjustContrast(d, k_contrast);
    c.rgb = d.rgb;
    o_color  = c;
    // basic black and white effet
    // float moyenne = (c.x + c.y + c.z)/3;
    // o_color = float4(moyenne, moyenne, moyenne, 1);
}

''', Shader.SL_Cg)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere')
    e = Entity(model='cube', y=-1)
    camera.shader = camera_contrast_shader
    camera.set_shader_input('contrast', 1)
    EditorCamera()

    app.run()
