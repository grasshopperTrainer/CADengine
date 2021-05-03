#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in float edge_thk;
layout (location = 2) in vec4 clr_edge;
layout (location = 3) in uint goid;

out vsOut {
    float edgeThk;
    vec4 edgeClr;
    uint goid;
} vs_out;

void main() {
    // for geometry shader
    vs_out.edgeThk = edge_thk;
    vs_out.edgeClr = clr_edge;
    vs_out.goid = goid;

    gl_Position = geo;
}