#version 450 core

in vec4 edgeClr;
in vec3 fcid;
in vec4 fcoord;

layout (location=0) out vec4 FragColor;
layout (location=1) out vec4 cid;
layout (location=2) out vec4 coord;

void main() {
    FragColor = edgeClr;
    cid = vec4(fcid, 1);
    coord = fcoord;
}
