#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 1) in vec4 clr;
layout (location = 2) in float dia;
layout (location = 3) in vec4 oid;

out vsOut {
    vec4 clr;
    float dia;
    vec4 oid;
} vs_out;

void main() {
    // as vector so
    vs_out.clr = clr;
    vs_out.dia = dia;
    vs_out.oid = oid;
    // transformation done in geometry shader
    gl_Position = vtx;
}
