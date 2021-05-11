#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in vec4 clr;
layout (location = 2) in float dia;
layout (location = 3) in vec3 goid;
layout (location = 4) in int goid_flag;

out vsOut {
    vec4 clr;
    vec4 goid;
    float dia;
} vs_out;

void main() {
    vs_out.clr = clr;
    vs_out.goid = vec4(goid, goid_flag);
    vs_out.dia = dia;
    // transformation done in geometry shader
    gl_Position = geo;
}
