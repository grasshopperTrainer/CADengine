#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in float edge_thk;
layout (location = 2) in vec4 edge_clr;
layout (location = 3) in vec4 oid;

out vsOut {
    float edgeThk;
    vec4 edgeClr;
    vec4 oid;
} vs_out;

void main() {
    // for geometry shader
    vs_out.edgeThk = edge_thk;
    vs_out.edgeClr = edge_clr;
    vs_out.oid = oid;

    gl_Position = geo;
}
