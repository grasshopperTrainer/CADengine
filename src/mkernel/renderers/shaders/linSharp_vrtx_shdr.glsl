#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 1) in float thk;
layout (location = 2) in vec4 clr;

out vsOut {
    float thk;
    vec4 clr;
} vs_out;

void main() {
    // as vector so
    vs_out.thk = thk;
    vs_out.clr = clr;
    // transformation done in geometry shader
    gl_Position = vtx;
}
