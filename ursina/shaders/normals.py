from panda3d.core import Shader


normals_shader = Shader.make('''

void vshader(float4 vtx_position : POSITION,
             // float4 vtx_color: COLOR,
             float3 vtx_normal: NORMAL,
             out float4 l_position : POSITION,
             out float3 l_norm0 : COLOR0,
             // out float4 l_norm : NORMAL,
             uniform float4x4 mat_modelproj,
             uniform float4x4 inv_modelview,

             uniform float4x4 mat_modelview,

             uniform float4x4 inv_projection,

             // uniform float rot_y
             uniform float4x4 transform_matrix
         )
{
    l_position = mul(mat_modelproj, vtx_position);
    // l_norm0 = float4(vtx_normal[0], vtx_normal[1], vtx_normal[2], 1);

    float4 invcamx = transform_matrix[0];
    float4 invcamy = transform_matrix[1];
    float4 invcamz = transform_matrix[2];
    float4 invcamw = transform_matrix[3];

    float3x3 invcam = float3x3(
                            invcamx[0], invcamx[1], invcamx[2],
                            invcamy[0], invcamy[1], invcamy[2],
                            invcamz[0], invcamz[1], invcamz[2]
                        );
    // float3x3 mat_modelproj = float3x3(mat_modelproj);

    float3 world_space_normal = normalize(mul(vtx_normal, invcam));
    // // vec3 world_space_normal = vec3(model_matrix * vec4(vertex_normal, 0.0));
    l_norm0 = float4(world_space_normal, 1.0);
    // l_norm0 = float3(vtx_normal[0], rot_y, vtx_normal[2]);


}

void fshader(
            float3 l_norm0 : COLOR0,
             out float4 o_color : COLOR)
{
  // o_color = l_color0.grba;
  // o_color = float4(1,0,1,1);
  // float r = v
  // o_color = l_norm0;
  // float3 normal = float3(l_norm0);
  // o_color = float4(dot(l_norm0, float3(0,1,0)), 1);
  o_color = float4(l_norm0*0.5+0.5, 1);
  // c.rgb = i.worldNormal*0.5+0.5;
}

''', Shader.SL_Cg)



if __name__ == '__main__':
    from ursina import *
    from ursina.prefabs.primitives import *
    app = Ursina()
    window.color=color.black

    # e = Entity(model='sphere', shader=normals_shader)
    # e.setShaderInput('transform_matrix', e.getNetTransform().getMat())
    shader = normals_shader

    a = WhiteCube(shader=shader)
    a.setShaderInput('transform_matrix', a.getNetTransform().getMat())

    b = AzureSphere(shader=shader, rotation_y=180, x=3)
    b.set_shader_input('transform_matrix', b.getNetTransform().getMat())
    # AzureSphere(shader=a.shader, y=2)
    GrayPlane(scale=10, y=-2, texture='shore')

    Sky(color=color.light_gray)
    EditorCamera()

    def update():
        b.rotation_y += 1
        b.set_shader_input('transform_matrix', b.getNetTransform().getMat())
        b.set_shader_input('test', 1)
    # EditorCamera()

    app.run()


    def shader_update(self):
        self.set_shader_input('transform_matrix', self.getNetTransform().getMat(), continuous=True)
