#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in float thk;
layout (location = 2) in vec4 clr;
layout (location = 3) in uint goid;
layout (location = 4) in int active_goid;

out vsOut {
    float thk;
    vec4 clr;
    uint goid;
} vs_out;

void main() {
    // as vector so
    vs_out.thk = thk;
    vs_out.clr = clr;
    vs_out.goid = goid * active_goid;
    // transformation done in geometry shader
    gl_Position = geo;
}
