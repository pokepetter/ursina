from ursina import *; ssao_shader = Shader(language=Shader.GLSL, fragment='''
#version 140


vec3 sphere[16] = vec3[](
    vec3( 0.5381, 0.1856,-0.4319), vec3( 0.1379, 0.2486, 0.4430),
    vec3( 0.3371, 0.5679,-0.0057), vec3(-0.6999,-0.0451,-0.0019),
    vec3( 0.0689,-0.1598,-0.8547), vec3( 0.0560, 0.0069,-0.1843),
    vec3(-0.0146, 0.1402, 0.0762), vec3( 0.0100,-0.1924,-0.0344),
    vec3(-0.3577,-0.5301,-0.4358), vec3(-0.3169, 0.1063, 0.0158),
    vec3( 0.0103,-0.5869, 0.0046), vec3(-0.0897,-0.4940, 0.3287),
    vec3( 0.7119,-0.0154,-0.0918), vec3(-0.0533, 0.0596,-0.5411),
    vec3( 0.0352,-0.0631, 0.5460), vec3(-0.4776, 0.2847,-0.0271)
);


uniform sampler2D tex;
uniform sampler2D dtex;
uniform sampler2D random_texture;
uniform mat4 p3d_ViewProjectionMatrix;

in vec2 uv;
out vec4 o_color;

uniform float numsamples;
uniform float radius;
uniform float amount;
uniform float strength;
uniform float falloff;


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

vec3 reconstructPosition(in vec2 uv, in float z)
{
    float x = uv.x * 2.0f - 1.0f;
    float y = (1.0 - uv.y) * 2.0f - 1.0f;
    vec4 position_s = vec4(x, y, z, 1.0f);
    mat4x4 view_projection_matrix_inverse = inverse(p3d_ViewProjectionMatrix);
    vec4 position_v = view_projection_matrix_inverse * position_s;
    return position_v.xyz / position_v.w;
}


void main() {
    float depth = texture(dtex, uv).r;
    vec3 position = reconstructPosition(uv, depth);
    vec3 normal = get_normal(uv);

    vec2 noiseScale = vec2(800.0/4.0, 600.0/4.0); // screen = 800x600
    vec3 randomVec = texture(random_texture, uv * noiseScale).xyz;
    vec3 tangent   = normalize(randomVec - normal * dot(randomVec, normal));
    vec3 bitangent = cross(normal, tangent);
    mat3 TBN       = mat3(tangent, bitangent, normal);

    vec3 random_vector = normalize((texture(random_texture, uv * 18.0 + depth + normal.xy).xyz * 2.0) - vec3(1.0)).xyz;
    float occlusion = 0.0;
    float radius = radius / depth;
    float depth_difference;
    vec3 sample_normal;
    vec3 ray;

    for(int i = 0; i < numsamples; ++i) {
        vec3 random_vector = texture(random_texture, uv * i * 100).xyz;
        ray = radius * reflect(sphere[i], random_vector);
        sample_normal = get_normal(uv + ray.xy).xzy;

        depth_difference = (depth - texture(dtex, uv + ray.xy).r);
        occlusion += step(falloff, depth_difference) * (.1 - dot(sample_normal.xyz, normal)) * (1.0 - smoothstep(falloff, strength, depth_difference));
    }

    o_color.rgb = normal;
    o_color.rgb = texture(tex, uv).rgb + (occlusion * -(amount/numsamples));
    o_color.a = 1.0;
}
''',

default_input = {
    'numsamples' : 16,
    'radius' : 0.01, # 0.05 is broken and cool
    'amount' : 3.0,
    'strength' : 0.001,
    'falloff' : 0.000002,
    'random_texture' : Func(load_texture, 'noise'),
}
)
if __name__ == '__main__':
    from ursina import *
    app = Ursina()

    e = Entity(model='sphere', color=color.orange)
    e = Entity(model='cube', y=-1)
    e = Entity(model='plane', scale=100, y=-1)
    camera.shader = ssao_shader
    #camera.clip_plane_far = 500
    camera.clip_plane_near = 1

    EditorCamera()

    def input(key):
        if key == 'space':
            if camera.shader:
                camera.shader = None
            else:
                camera.shader = ssao_shader


    random.seed(2)
    for i in range(20):
        e = Entity(model='cube', position=Vec3(random.random(),random.random(),random.random())*3, rotation=Vec3(random.random(),random.random(),random.random())*360)
        # e.shader = matcap_shader
    app.run()
