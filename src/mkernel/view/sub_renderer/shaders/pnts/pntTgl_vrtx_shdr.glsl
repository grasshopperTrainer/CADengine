#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in vec4 clr;
layout (location = 2) in float dia;
layout (location = 3) in vec4 oid;

out vsOut {
    vec4 oid;
    vec4 clr;
    float dia;
} vs_out;

void main() {
    vs_out.oid = oid;
    // as vector so
    vs_out.clr = clr;
    vs_out.dia = dia;
    // transformation done in geometry shader
    gl_Position = geo;
}
