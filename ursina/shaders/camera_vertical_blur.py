from panda3d.core import Shader


camera_vertical_blur_shader = Shader.make('''

void vshader(float4 vtx_position : POSITION,
            // float2 vtx_texcoord0 : TEXCOORD0,
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
             uniform sampler2D k_tex : TEXUNIT0,
             uniform float k_blur_size)
{
    float4 c = tex2D(k_tex, l_texcoord0);
    float4 col = 0;
    for(float index=0;index<10;index++){
            //add color at position to color
            float2 uv = l_texcoord0 + float2(0, (index/9 - 0.5) * k_blur_size);
            col += tex2D(k_tex, uv);
        }
    col = col / 10;
    // o_color = col;
    float r = 1-((1-col[0])*(1-c[0]));
    float g = 1-((1-col[1])*(1-c[1]));
    float b = 1-((1-col[2])*(1-c[2]));
    // 1-((1-c)*(1-col))
    o_color = float4(r,g,b,1);
    // basic black and white effet
    // float moyenne = (c.x + c.y + c.z)/3;
    // o_color = float4(moyenne, moyenne, moyenne, 1);
}

''', Shader.SL_Cg)



if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    window.color = color._16

    e = Entity(model='sphere', color=color.orange)
    e = Entity(model='cube', y=-1)
    camera.shader = camera_vertical_blur_shader
    camera.set_shader_input("blur_size", .05)


    slider = ThinSlider(max=.1, dynamic=True, position=(-.25, -.45))

    def set_blur():
        camera.set_shader_input("blur_size", slider.value)

    slider.on_value_changed = set_blur
    EditorCamera()

    app.run()
