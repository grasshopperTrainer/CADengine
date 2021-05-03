#version 450 core

in gsOut {
    flat uint goid;
    vec4 clr;
    vec4 coord;
} gs_in;

layout (location=0) out vec4 fclr;
layout (location=1) out uint goid;
layout (location=2) out vec4 fcoord;

void main() {
    fclr = gs_in.clr;
    goid = gs_in.goid;
    fcoord = gs_in.coord;
}
