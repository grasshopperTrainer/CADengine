#version 450 core

in vec4 edgeClr;
in vec4 oid;

layout (location = 0) out vec4 fclr;
layout (location = 1) out vec4 foid;

void main() {
    fclr = edgeClr;
    foid = oid;
}
