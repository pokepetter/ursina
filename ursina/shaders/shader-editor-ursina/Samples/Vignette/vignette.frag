#version 430

float distance_from_center(vec2 v){
    return length(v - vec2(0.5));
}

uniform sampler2D tex;
uniform float vignette_distance=.2;
uniform vec4 vignette_color=vec4(0);//color
uniform float vignette_density=1.;
in vec2 uv;
out vec4 color;
void main() {
    float d = distance_from_center(uv);
    vec4 initial_color = texture(tex, uv);
    if (d > vignette_distance) {
        color = mix(initial_color, vignette_color, (d - vignette_distance) * pow(vignette_density,2));
    }
    else {
        color = initial_color;
    }
}