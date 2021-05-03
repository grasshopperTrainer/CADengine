#version 450 core

in vec4 fclr;
in vec4 foid;
in vec4 fcoord;

layout (location=0) out vec4 clr;
layout (location=1) out uint goid;
layout (location=2) out vec4 coord;

void main() {
    clr = fclr;
    goid = foid;
    coord = fcoord;
}
