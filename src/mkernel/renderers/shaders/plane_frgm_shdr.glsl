#version 450 core

in vec4 fclr;
in vec3 fcid;

layout (location=0) out vec4 clr;
layout (location=1) out vec4 cid;

void main() {
    clr = fclr;
    cid = vec4(fcid, 1);
}
