#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in float edge_thk;
layout (location = 2) in vec4 clr_edge;
layout (location = 3) in vec3 goid;
layout (location = 4) in int goid_flag;

out vsOut {
    float edgeThk;
    vec4 edgeClr;
    vec4 goid;
} vs_out;

void main() {
    // for geometry shader
    vs_out.edgeThk = edge_thk;
    vs_out.edgeClr = clr_edge;
    vs_out.goid = vec4(goid, goid_flag);

    gl_Position = geo;
}
