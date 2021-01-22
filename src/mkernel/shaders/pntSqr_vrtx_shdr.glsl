#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 1) in vec4 clr;
layout (location = 2) in float dia;

out vsOut {
    vec4 clr;
    float dia;
} vs_out;

void main() {
    // as vector so
    vs_out.clr = clr;
    vs_out.dia = dia;
    // transformation done in geometry shader
    gl_Position = vtx;
}
