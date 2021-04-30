#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in float thk;
layout (location = 2) in vec4 clr;
layout (location = 3) in vec4 oid;

out vsOut {
    float thk;
    vec4 clr;
    vec4 oid;
} vs_out;

void main() {
    // as vector so
    vs_out.thk = thk;
    vs_out.clr = clr;
    vs_out.oid = oid;
    // transformation done in geometry shader
    gl_Position = geo;
}
