#version 450 core

in vec4 clr;
flat in uint goid;
in vec4 coord;

layout(location=0) out vec4 fclr;
layout(location=1) out uint id_clr;
layout(location=2) out vec4 fcoord;

void main() {
    fclr = clr;
    id_clr = goid;
    fcoord = coord;
}
