#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in float thk;
layout (location = 2) in vec4 clr;
layout (location = 3) in vec3 goid;
layout (location = 4) in int goid_flag;

out vsOut {
    float thk;
    vec4 clr;
    vec4 goid;
} vs_out;

void main() {
    // as vector so
    vs_out.thk = thk;
    vs_out.clr = clr;
    vs_out.goid = vec4(goid, goid_flag);
    // transformation done in geometry shader
    gl_Position = geo;
}
