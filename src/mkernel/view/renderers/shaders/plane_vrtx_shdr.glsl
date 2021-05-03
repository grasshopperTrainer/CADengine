#version 450 core

// plane description, since in mat4 feels ambiguous...
layout (location=0) in vec4 ori;
layout (location=1) in vec4 x;
layout (location=2) in vec4 y;
layout (location=3) in vec4 z;

layout (location=4) in float len;
layout (location=5) in uint goid;

out vsOut {
    mat4 pln;
    float len;
    uint goid;
} vs_out;

void main() {
    // vector to points
    vs_out.pln = mat4(ori, x, y, z);
    vs_out.len = len;
    vs_out.goid = goid;
    gl_Position = ori;   // column major?
}