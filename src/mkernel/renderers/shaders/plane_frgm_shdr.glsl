#version 450 core

in vec4 fclr;
in vec4 foid;

layout (location=0) out vec4 clr;
layout (location=1) out vec4 oid;

void main() {
    clr = fclr;
    oid = foid;
}
