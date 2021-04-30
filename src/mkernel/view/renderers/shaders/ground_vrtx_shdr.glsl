#version 450 core

layout (location=0) in vec3 pos;
layout (location=1) in vec3 near;
layout (location=2) in vec3 far;
layout (location=3) in vec4 clr;

out vec3 fnear;
out vec3 ffar;
out vec4 fclr;

void main() {
    fnear = near;
    ffar = far;
    fclr = clr;
    gl_Position = vec4(pos, 1);
}
