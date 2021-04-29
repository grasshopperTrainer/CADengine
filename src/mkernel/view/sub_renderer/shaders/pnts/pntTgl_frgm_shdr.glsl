#version 450 core

in gsOut {
    vec4 oid;
    vec4 clr;
    vec4 coord;
} gs_in;

layout (location=0) out vec4 fclr;
layout (location=1) out vec4 oid;
layout (location=2) out vec4 fcoord;

void main() {
    fclr = gs_in.clr;
    oid = gs_in.oid;
    fcoord = gs_in.coord;
}
