#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 1) in float thk;
layout (location = 2) in vec4 clr;
layout (location = 3) in vec3 cid;

out vsOut {
    float thk;
    vec4 clr;
    vec3 cid;
} vs_out;

void main() {
    // as vector so
    vs_out.thk = thk;
    vs_out.clr = clr;
    vs_out.cid = cid;
    // transformation done in geometry shader
    gl_Position = vtx;
}
