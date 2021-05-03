#version 450 core

in vec4 fclr;
flat in uint foid;
in vec4 fcoord;

layout (location=0) out vec4 fragClr;
layout (location=1) out uint goid;
layout (location=2) out vec4 coord;

void main() {
    fragClr = fclr;
    goid = foid;
    coord = fcoord;
}
