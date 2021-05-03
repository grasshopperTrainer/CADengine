#version 450 core

in vec4 fclr;
flat in uint foid;

layout (location=0) out vec4 clr;
layout (location=1) out uint goid;

void main() {
    clr = fclr;
    goid = foid;
}
