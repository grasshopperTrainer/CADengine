#version 450 core

in gsOut {
    vec4 edgeClr;
    vec4 goid;
} fs_in;

layout (location = 0) out vec4 clr;
layout (location = 1) out vec4 goid;

void main() {
    clr = fs_in.edgeClr;
    goid = fs_in.goid;
}
