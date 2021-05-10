#version 450 core

in gsOut {
    vec4 clr;
    flat uvec3 goid;
    vec4 coord;
} gs_in;

layout (location=0) out vec4 fclr;
layout (location=1) out uvec4 goid;
layout (location=2) out vec4 fcoord;

void main() {
    fclr = gs_in.clr;
    goid = uvec4(gs_in.goid, 1);
    fcoord = gs_in.coord;
}
