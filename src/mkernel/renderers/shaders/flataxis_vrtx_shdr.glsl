#version 450 core

// simple full surface rec draw
layout (location=0) in vec2 pos;
layout (location=1) in vec4 ori;
layout (location=2) in vec4 dir;
layout (location=3) in float thk;

// camera near plane corner coordinates
layout (location=4) in vec4 ncoord;
layout (location=5) in vec4 fcoord;

out vsAttr {
    vec3 ori;
    vec3 dir;
    vec3 ncoord;
    vec3 fcoord;
    vec3 coord;
    float thk;
} vs_out;

void main() {
    vs_out.ori = ori.xyz;
    vs_out.dir = dir.xyz;
    vs_out.ncoord = ncoord.xyz;
    vs_out.fcoord = fcoord.xyz;
    vs_out.coord = vec3(pos, 0);
    vs_out.thk = thk;

    gl_Position = vec4(pos, 0, 1);
}
