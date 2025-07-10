from ursina import Shader

curvature_shader = Shader(
fragment='''
#version 430
#extension GL_OES_standard_derivatives : enable

uniform mat4 p3d_ProjectionMatrix;
uniform mat4 p3d_ViewProjectionMatrix;
// uniform mat4 view_projection_matrix_inverse;

uniform sampler2D tex;
uniform sampler2D dtex;
// uniform sampler2D ntex;
in vec2 uv;
out vec4 color;

vec3 reconstructPosition(in vec2 uv, in float z)
{
    float x = uv.x * 2.0f - 1.0f;
    float y = (1.0 - uv.y) * 2.0f - 1.0f;
    vec4 position_s = vec4(x, y, z, 1.0f);
    mat4x4 view_projection_matrix_inverse = inverse(p3d_ViewProjectionMatrix);
    vec4 position_v = view_projection_matrix_inverse * position_s;
    return position_v.xyz / position_v.w;
}
// vec3 reconstructPosition(in vec2 uv, float depth) {
//     float z = depth * 2.0 - 1.0;
//
//     vec4 clipSpacePosition = vec4(uv * 2.0 - 1.0, z, 1.0);
//     vec4 viewSpacePosition = inverse(p3d_ViewProjectionMatrix) * clipSpacePosition;
//
//     // Perspective division
//     viewSpacePosition /= viewSpacePosition.w;
//
//     vec4 worldSpacePosition = inverse(p3d_ViewProjectionMatrix) * viewSpacePosition;
//
//     return worldSpacePosition.xyz;
// }

vec3 get_normal(vec2 texcoords) {
    const vec2 offset1 = vec2(0.0, 0.001);
    const vec2 offset2 = vec2(0.001, 0.0);

    float depth = texture(dtex, texcoords).r;
    float depth1 = texture(dtex, texcoords + offset1).r;
    float depth2 = texture(dtex, texcoords + offset2).r;

    vec3 p1 = vec3(offset1, depth1 - depth);
    vec3 p2 = vec3(offset2, depth2 - depth);

    vec3 normal = cross(p1, p2);
    normal.z = -normal.z;

    return normalize(normal);
}

void main() {
    float z = texture(dtex, uv).r;
    // depth = depth*depth;
    vec3 position = reconstructPosition(uv, z);
    vec3 n = get_normal(uv);
    // n = normalize(cross(dFdx(position), dFdy(position)));
    // n.z *= -1;
    // n.y *= -1;
    // n = n * vec3(1, -1, 1);
    n = vec3(n.xyz * 0.5f + 0.5f) * 0.5;


    // color = texture(dtex, uv).rgba;
// Compute curvature
    vec3 dx = dFdx(n);
    vec3 dy = dFdy(n);
    vec3 xneg = n - dx;
    vec3 xpos = n + dx;
    vec3 yneg = n - dy;
    vec3 ypos = n + dy;
    float depth = z;
    float curvature = (cross(xneg, xpos).y - cross(yneg, ypos).x) * 4.0 / depth;

    // Compute surface properties
    vec3 light = vec3(0.0);
    vec3 ambient = vec3(curvature + 0.5);
    // vec3 diffuse = vec3(0.0);
    // vec3 specular = vec3(0.0);
    // float shininess = 0.0;

    // Compute final color
    float cosAngle = dot(n, light);
    // if (ambient.r > .6 || ambient.r < .1) {
    //     ambient = vec3(0., 0., 0.);
    // }
    // color.rgb = ambient + diffuse * max(0.0, cosAngle) + specular * pow(max(0.0, cosAngle), shininess);
    color.rgb = ambient;
    // color.rgb = n;
    // color.rgb = vec3(depth);
}
''')



if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere', color=color.orange)
    e = Entity(model='cube', y=-1)
    camera.shader = curvature_shader
    camera.clip_plane_near = 1
    # camera.clip_plane_far = 1000
    # camera.set_shader_input('contrast', 1)
    EditorCamera()
    #
    # def input(key):
    #     if key == 'space':
    #         if hasattr(camera, '_shader') and camera.shader:
    #             camera.shader = None
    #         else:
    #             camera.shader = curvature_shader
    # # from ursina.shaders import matcap_shader

    random.seed(2)
    for i in range(20):
        e = Entity(model='cube', position=Vec3(random.random(),random.random(),random.random())*2, rotation=Vec3(random.random(),random.random(),random.random())*360)
        # e.shader = matcap_shader
        # e.texture='blender_matcap'
        # e.model.generate_normals()
    #
    # tp = loader.loadModel('teapot')
    # tp.reparentTo(scene_root)
    # tp.setPos(-2, 2, 0)
    # tp.setScale(0.5)

    # depthTexture = PandaTexture("depthTexture")
    # depthTexture.set_format(PandaTexture.F_depth_component32)
    #
    # depthBuffer = base.win.make_texture_buffer("depthBuffer", 0, 0, depthTexture);
    # depthBuffer.set_clear_color(LVecBase4f(0, 0, 0, 0));
    # # #
    # depthCameraNP = camera._cam
    # # DCAST(Camera, depthCameraNP.node())->set_lens(window->get_camera(0)->get_lens());
    # depthBufferRegion = depthBuffer.make_display_region(0, 1, 0, 1);
    # depthBufferRegion.set_camera(base.cam);
    # # depthTexture = PandaTexture("depthTexture")
    # camera.set_shader_input('dtex', depthTexture)
    # Entity(model='quad', texture=depthTexture)
     # Needed for camera depth image

     # from panda3d.core import Texture as PandaTexture
     # from panda3d.core import LVecBase4f
    # from panda3d.core import FrameBufferProperties, WindowProperties
    # from panda3d.core import GraphicsPipe, GraphicsOutput
    # winprops = window
    # fbprops = FrameBufferProperties()
    # fbprops.setDepthBits(1)
    # app.depthBuffer = app.graphicsEngine.makeOutput(
    #     app.pipe, "depth buffer", -2,
    #     fbprops, winprops,
    #     GraphicsPipe.BFRefuseWindow,
    #     app.win.getGsg(), app.win)
    # app.depthTex = PandaTexture()
    # app.depthTex.setFormat(PandaTexture.FDepthComponent)
    # app.depthBuffer.addRenderTexture(app.depthTex,
    #     GraphicsOutput.RTMCopyRam, GraphicsOutput.RTPDepth)
    # lens = base.cam.node().getLens()
    # # the near and far clipping distances can be changed if desired
    # lens.setNear(2.0)
    # # lens.setFar(500.0)
    # app.depthCam = app.makeCamera(app.depthBuffer,
    #     lens=lens,
    #     scene=render)
    # app.depthCam.reparentTo(base.cam)
    # camera.set_shader_input('dtex', app.depthTex)
    #
    # # def input(key):
    # #     if key == 'space':
    # #         lens.setNear(2.0)


    app.run()
