#version 430

uniform sampler2D tex;
uniform bool invert=true;
uniform int power=100;//(0,100)
in vec2 uv;
out vec4 color;

void main() {
    vec3 rgb = texture(tex, uv).rgb;
	if (invert){
        color = vec4(abs(rgb-(power/100.0)), 1.0);
    }
    else{
        color = vec4(rgb,1.0);
    }
}