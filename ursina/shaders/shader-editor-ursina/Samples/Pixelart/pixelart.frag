#version 430

uniform sampler2D tex;
uniform float osg_FrameTime;
uniform vec2 pixel_size=vec2(10,10);
uniform float palette_size=4;
uniform float spread=0.23;
uniform float gamma_correction=2.2;

vec3 dithering(vec3 color,vec2 uv){
    mat4 dither_matrix = mat4(0, 8, 2, 10, 
                              12, 4, 14, 6,
                              3, 11, 1, 9,
                              15, 7, 13, 5) * 0.0625;
     
    vec2 xy = mod((uv*textureSize(tex,0)),4);
    float dither = dither_matrix[int(xy.x)][int(xy.y)];
    color = clamp(color + spread * dither-1/2, 0.0, 1.0);
    return color;
}

vec3 gamma_cor(vec3 color,float gamma){
    return pow(color,vec3(gamma*100));
}

vec3 apply_palette(vec3 color){
    return floor(color*(palette_size-1)+0.5)/(palette_size-1);
}

vec3 getColor(vec2 adapted_uv,vec2 uv){
    return apply_palette(gamma_cor(dithering(texture(tex, adapted_uv).rgb,adapted_uv),gamma_correction));
}

in vec2 uv;
out vec4 fragColor;
void main() {
    vec2 offset = mod(uv, (pixel_size* 1/textureSize(tex, 0))); 
    
    vec2 adapted_uv = uv - offset;


    vec3 color = getColor(adapted_uv,uv);

    fragColor =vec4(color,1);

}