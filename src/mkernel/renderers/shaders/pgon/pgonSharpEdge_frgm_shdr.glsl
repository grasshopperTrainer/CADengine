#version 450 core

in vec4 edgeClr;
in vec3 cid;

layout (location = 0) out vec4 fclr;
layout (location = 1) out vec4 fcid;

void main() {
    fclr = edgeClr;
    fcid = vec4(cid, 1);
}
