#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 1) in float edge_thk;
layout (location = 2) in vec4 edge_clr;
layout (location = 3) in vec4 fill_clr;
layout (location = 4) in vec4 oid;

layout (location = 0) uniform mat4 PM;
layout (location = 1) uniform mat4 VM;
layout (location = 2) uniform mat4 MM = mat4(1.0);

out vsOut {
    float edgeThk;
    vec4 edgeClr;
    vec4 fillClr;
    vec4 oid;
} vs_out;

void main() {
    // for geometry shader
    vs_out.edgeThk = edge_thk;
    vs_out.edgeClr = edge_clr;
    vs_out.fillClr = fill_clr;
    vs_out.oid = oid;

    gl_Position = vtx;
}
