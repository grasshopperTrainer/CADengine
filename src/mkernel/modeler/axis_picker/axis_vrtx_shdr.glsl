#version 450 core

// simple full surface rec draw
layout (location=0) in vec4 ori;
layout (location=1) in vec4 dir;
layout (location=2) in float thk;
layout (location=3) in vec3 cid;
layout (location=4) in vec2 pos;

// camera near plane corner coordinates
layout (location=5) in vec4 ncoord;
layout (location=6) in vec4 fcoord;

out vsAttr {
    vec3 ori;
    vec3 dir;
    vec3 ncoord;
    vec3 fcoord;
    vec3 coord;
    float thk;
    vec3 cid;
} vs_out;

void main() {
    vs_out.ori = ori.xyz;
    vs_out.dir = dir.xyz;
    vs_out.ncoord = ncoord.xyz;
    vs_out.fcoord = fcoord.xyz;
    vs_out.coord = vec3(pos, 0);
    vs_out.thk = thk;
    vs_out.cid = cid;

    gl_Position = vec4(pos, 0, 1);
}
