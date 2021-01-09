from ursina import *; screen_space_normals_shader = Shader(language=Shader.GLSL, fragment='''
#version 140

uniform vec4 p3d_ColorScale;
in vec2 uv;
out vec4 fragColor;
in vec3 world_normal;
uniform sampler2D tex;
uniform sampler2D dtex;
uniform mat4 p3d_ProjectionMatrixInverse;

vec3 World_position_from_depth(in float depth, in vec2 uv){
    vec2 st_ = uv * 2.0 - 1.0;  //translate 0s at the center of the image, range [-1,1]
    depth =  depth * 2.0 - 1.0; //do the same for depth values

    vec4 clipSpacePosition =  vec4(st_.x, st_.y, depth, 1.);
    vec4 viewSpacePosition = p3d_ProjectionMatrixInverse  * clipSpacePosition;
    viewSpacePosition /= viewSpacePosition.w;      // Perspective division
    return viewSpacePosition.xyz;
}

vec3 normal_from_depth(float depth, vec2 texcoords) {
  const vec2 offset1 = vec2(0.0,0.001);
  const vec2 offset2 = vec2(0.001,0.0);

  float depth1 = texture(dtex, texcoords + offset1).r;
  float depth2 = texture(dtex, texcoords + offset2).r;

  vec3 p1 = vec3(offset1, depth1 - depth);
  vec3 p2 = vec3(offset2, depth2 - depth);

  vec3 normal = cross(p1, p2);
  normal.z = -normal.z;

  // return normal;
  return normalize(normal);
}

const float total_strength = 1.0;
const float base = 0.2;

const float area = 0.0075;
const float falloff = 0.000001;

const float radius = 0.0002;

const int samples = 16;
vec3 sample_sphere[samples] = vec3[](
    vec3( 0.5381, 0.1856,-0.4319), vec3( 0.1379, 0.2486, 0.4430),
    vec3( 0.3371, 0.5679,-0.0057), vec3(-0.6999,-0.0451,-0.0019),
    vec3( 0.0689,-0.1598,-0.8547), vec3( 0.0560, 0.0069,-0.1843),
    vec3(-0.0146, 0.1402, 0.0762), vec3( 0.0100,-0.1924,-0.0344),
    vec3(-0.3577,-0.5301,-0.4358), vec3(-0.3169, 0.1063, 0.0158),
    vec3( 0.0103,-0.5869, 0.0046), vec3(-0.0897,-0.4940, 0.3287),
    vec3( 0.7119,-0.0154,-0.0918), vec3(-0.0533, 0.0596,-0.5411),
    vec3( 0.0352,-0.0631, 0.5460), vec3(-0.4776, 0.2847,-0.0271)
);

uniform sampler2D random_texture;
vec3 random = normalize(texture(random_texture, uv * 4.0).rgb);

vec3 reconstructPosition(in vec2 uv, in float z)
{
  float x = uv.x * 2.0f - 1.0f;
  float y = (1.0 - uv.y) * 2.0f - 1.0f;
  vec4 position_s = vec4(x, y, z, 1.0f);
  vec4 position_v = p3d_ProjectionMatrixInverse * position_s;
  return position_v.xyz / position_v.w;
}

void main() {
    float depth = texture2D(dtex, uv).r;
    vec3 position = reconstructPosition(uv, depth);
    vec3 normal = normalize(cross(dFdx(position), dFdy(position)));
    // normal = normal_from_depth(depth, uv);
    fragColor = vec4(normal, 1);
}

''',
)


if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere', color=color.orange)
    e = Entity(model='cube', y=-1)
    e = Entity(model='plane', scale=100, y=-1)
    #camera.clip_plane_far = 100
    camera.shader = screen_space_normals_shader
    EditorCamera()

    def input(key):
        if key == 'space':
            if camera.shader:
                camera.shader = None
            else:
                camera.shader = screen_space_normals_shader

    app.run()
