#version 450 core

in vec4 clr;
in vec4 oid;
in vec4 coord;

layout(location=0) out vec4 fclr;
layout(location=1) out vec4 id_clr;
layout(location=2) out vec4 fcoord;

void main() {
    fclr = clr;
    id_clr = oid;
    fcoord = coord;
}
