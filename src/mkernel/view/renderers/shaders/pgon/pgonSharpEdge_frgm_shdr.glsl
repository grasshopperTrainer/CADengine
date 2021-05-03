#version 450 core

in vec4 edgeClr;
flat in uint goid;

layout (location = 0) out vec4 fclr;
layout (location = 1) out uint foid;

void main() {
    fclr = edgeClr;
    foid = goid;
}
