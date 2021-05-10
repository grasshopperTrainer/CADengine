#version 450 core


in gsOut {
    vec4 clr;
    flat uint oid;
    vec4 coord;
} fs_in;


layout (location = 0) out vec4 clr;
layout (location = 1) out uint goid;
layout (location = 2) out vec4 coord;

void main() {
    clr = fs_in.clr;
    goid = fs_in.oid;
    coord = fs_in.coord;
}
