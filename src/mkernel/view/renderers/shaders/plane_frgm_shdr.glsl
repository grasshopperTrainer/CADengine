#version 450 core

in vec4 fclr;
in vec4 foid;

layout (location=0) out vec4 clr;
layout (location=1) out vec4 goid;

void main() {
    clr = fclr;
    goid = foid;
}
