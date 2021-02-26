#version 450 core

layout (location=0) uniform mat4 PM;
layout (location=1) uniform mat4 VM;
//layout (location=1) uniform mat4 MM = mat4(1.0);

in vec3 fpos;
in vec3 fnear;
in vec3 ffar;
in vec4 fclr;

layout (location=0) out vec4 clr;

float compute_depth(vec3 P) {
    vec4 ndc_p = PM * VM * vec4(P, 1);
    float depth = ndc_p.z/ndc_p.w;
    float f = gl_DepthRange.far;
    float n = gl_DepthRange.near;
    float d = gl_DepthRange.diff;
    depth = n + (f - n) * (depth + 1)/2.0;
    return depth;
}

void main() {
    // reference:
    // https://github.com/martin-pr/possumwood/wiki/Infinite-ground-plane-using-GLSL-shaders
    // for each pixel find ray amplifier t where y is 0
    // this tells ray intersecting ground
    // 0 = near + t*(far - near)
    vec3 ray = (ffar - fnear);
    float r = -fnear.z / ray.z;
    vec3 P = fnear + r*ray;// intersection Point

    float ps = 1./10.;// chess pattern size
    // clamping resulted to 0.3 ~ 1
    float c = int(round(P.x * ps) + round(P.y * ps)) % 2;
    c = c*0.5 + 0.5;

    // soft horizon; use distance from camera near on xy
    float d = distance(fnear.xy, P.xy);
    float t0 = 100.;
    float t1 = 1000.;
    float l = max(0, min(1., (t1-d)/(t1-t0)));
    if (r < 0) discard;// negative t means ground is behind camera; meaning sky
    // blending rgb
    clr = vec4(fclr.xyz * c * l, 1);
    gl_FragDepth = compute_depth(P);
}
