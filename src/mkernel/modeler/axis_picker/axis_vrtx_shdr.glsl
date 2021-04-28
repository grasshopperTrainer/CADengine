#version 450 core

// simple full surface rec draw
layout (location=0) in vec4 ori;
layout (location=1) in vec4 dir;
layout (location=2) in float thk;
layout (location=3) in vec4 oid;


out vsAttr {
    vec3 ori;
    vec3 dir;
    float thk;
    vec4 oid;
} vs_out;

void main() {
    vs_out.ori = ori.xyz;
    vs_out.dir = dir.xyz;
    vs_out.thk = thk;
    vs_out.oid = oid;
}
