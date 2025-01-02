from ursina import Shader, Vec2
from ursina.shaders.unlit_shader import unlit_shader
vertex_animation_shader = Shader(
vertex='''
#version 330 core

uniform mat4 p3d_ModelViewProjectionMatrix;
in vec4 p3d_Vertex;
in vec2 p3d_MultiTexCoord0;
out vec2 uvs;
uniform vec2 texture_scale;
uniform vec2 texture_offset;

in vec4 p3d_Color;
out vec4 vertex_color;


uniform sampler2D frameTexture; // Texture containing all animation frames
uniform float frameIndex;       // Current animation frame (e.g., 1.3 for interpolation)
uniform float totalFrames;      // Total number of frames
uniform vec3 pos_min;
uniform vec3 pos_max;
uniform float num_verts;


out vec4 vertexColor;

void main() {
    // float frame_floor = floor(frameIndex);
    // float frameFrac = fract(frameIndex); // Fractional part for blending

    // // Calculate texture coordinates for current and next frames
    float frame_height = 1.0 / totalFrames; // Each frame's height in the texture
    // vec2 uvBase = vec2(gl_VertexID/, frame_floor * frame_height);
    // vec2 uvNext = vec2(gl_VertexID, (frame_floor + 1.0) * frame_height);

    // // Sample normalized offsets
    // vec3 offsetBase = texture(frameTexture, uvBase).rgb * 2.0 - 1.0; // Map [0, 1] to [-1, 1]
    // vec3 offsetNext = texture(frameTexture, uvNext).rgb * 2.0 - 1.0; // Map [0, 1] to [-1, 1]

    vec3 pos_offset = texture(frameTexture, vec2((gl_VertexID/num_verts) + ((1./num_verts)*.5), (frameIndex/totalFrames) + (frame_height*.5))).rgb;
    vec3 denormalized_pos_offset = mix(pos_min, pos_max, pos_offset.xyz);

    //vec3 pos_offset = texture(frameTexture, vec2(p3d_MultiTexCoord0.x, (frameIndex/totalFrames) + (frame_height*.5))).rgb;
    // // Interpolate offsets
    // vec3 interpolatedOffset = mix(offsetBase, offsetNext, frameFrac);

    // // Apply offset to the vertex position
    // vec3 animatedPosition = p3d_Vertex.xyz + interpolatedOffset;

    // Output position
    gl_Position = p3d_ModelViewProjectionMatrix * vec4(denormalized_pos_offset, 1.0);

    // Debug: output the offset as color
    //vertex_color = vec4(denormalized_pos_offset * 0.5 + 0.5, 1.0);
    uvs = (p3d_MultiTexCoord0 * texture_scale) + texture_offset;
    vertex_color = p3d_Color;
}    

''',

fragment='''
#version 330 core

uniform sampler2D p3d_Texture0;
uniform vec4 p3d_ColorScale;
in vec2 uvs;
out vec4 fragColor;

in vec4 vertex_color;

void main() {
    vec4 color = texture(p3d_Texture0, uvs) * p3d_ColorScale * vertex_color;
    fragColor = color.rgba;
}

''',
default_input = {
    'texture_scale' : Vec2(1,1),
    'texture_offset' : Vec2(0.0, 0.0),

    'frameIndex': 0,
}
)


if __name__ == '__main__':
    from ursina import *
    app = Ursina()
    e = Entity(model='cube', shader=vertex_animation_shader, texture='grass')
    animation_texture = load_texture('grass')
    e.set_shader_input('totalFrames', animation_texture.height)
    e.set_shader_input('num_verts', animation_texture.width)
    e.set_shader_input('frameTexture', animation_texture)

    e.set_shader_input('pos_min', Vec3(-.5,-.5,-.5))
    e.set_shader_input('pos_max', Vec3(.5,.5,.5))
    EditorCamera()

    e.animate_shader_input('frameIndex', 10, duration=3, loop=True)

    app.run()