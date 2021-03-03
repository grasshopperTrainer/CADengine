#version 450 core

in vec4 clr;

layout (location=0) out vec4 fclr;

void main() {
    fclr = clr;
}
