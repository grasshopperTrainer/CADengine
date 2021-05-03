#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 1) in float edge_thk;
layout (location = 2) in vec4 clr_edge;
layout (location = 3) in vec4 clr_fill;
layout (location = 4) in vec4 goid;

layout (location = 0) uniform mat4 PM;
layout (location = 1) uniform mat4 VM;
layout (location = 2) uniform mat4 MM = mat4(1.0);

out vsOut {
    float edgeThk;
    vec4 edgeClr;
    vec4 fillClr;
    vec4 goid;
} vs_out;

void main() {
    // for geometry shader
    vs_out.edgeThk = edge_thk;
    vs_out.edgeClr = clr_edge;
    vs_out.fillClr = clr_fill;
    vs_out.goid = goid;

    gl_Position = geo;
}
