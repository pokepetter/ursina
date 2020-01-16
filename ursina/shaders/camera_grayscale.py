from panda3d.core import Shader


camera_grayscale_shader = Shader.make('''

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


void fshader(float2 l_texcoord0 : TEXCOORD0,
             out float4 o_color : COLOR,
             uniform sampler2D k_tex : TEXUNIT0)
{
    float4 c = tex2D(k_tex, l_texcoord0);

    float gray = (c.x + c.y + c.z)/3;
    o_color = float4(gray, gray, gray, 1);
}

''', Shader.SL_Cg)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere', color=color.orange)
    e = Entity(model='cube', y=-1)
    camera.shader = camera_grayscale_shader
    # camera.set_shader_input('contrast', 1)
    EditorCamera()

    app.run()
