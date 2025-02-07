#version 430

//Not my algorithm !! 
//Ported from shadertoy :
//https://www.shadertoy.com/view/4s2GRR


uniform float fishyness=0.2;
in vec2 uv;
uniform sampler2D p3d_Texture0;
out vec4 fragColor;
void main()
{
        vec2 resolution = textureSize(p3d_Texture0,0);
	vec2 p = uv*resolution/resolution.x;
        float prop = resolution.x/resolution.y;
	vec2 m = vec2(0.5, 0.5 / prop);
	vec2 d = p - m;
	float r = sqrt(dot(d, d));
 	float power = ( 2.0 * 3.141592 / (2.0 * sqrt(dot(m, m))) ) * fishyness;
	float bind;
	if (power > 0.0) bind = sqrt(dot(m, m));
	else {if (prop < 1.0) bind = m.x; else bind = m.y;}
 	vec2 adapted_uv;
	if (power > 0.0)//fisheye
		adapted_uv = m + normalize(d) * tan(r * power) * bind / tan( bind * power);
	else if (power < 0.0)//antifisheye
		adapted_uv = m + normalize(d) * atan(r * -power * 10.0) * bind / atan(-power * bind * 10.0);
	else adapted_uv = p;//no effect for fishyness = 0.0

	vec3 col = texture(p3d_Texture0, vec2(adapted_uv.x, -adapted_uv.y * prop)).xyz;
	fragColor = vec4(col, 1.0);
}