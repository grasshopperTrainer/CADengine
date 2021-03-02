#version 450 core

layout (location=0) in vec2 pos;
layout (location=1) in vec4 clr;
layout (location=2) in float dim;

out vec4 aclr;

void main() {
    aclr = clr;
    gl_PointSize = dim;
    gl_Position = vec4(pos, -1, 1);
}