#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in vec4 clr;
layout (location = 2) in float dia;
layout (location = 3) in vec4 goid;

out vsOut {
    vec4 clr;
    float dia;
    vec4 goid;
} vs_out;

void main() {
    // as vector so
    vs_out.clr = clr;
    vs_out.dia = dia;
    vs_out.goid = goid;
    // transformation done in geometry shader
    gl_Position = geo;
}
