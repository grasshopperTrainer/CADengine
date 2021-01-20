#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 1) in vec4 clr_edge;

layout (location = 0) uniform mat4 MM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 PM = mat4(1.0);

out vec4 fClrEdge;

void main() {
    fClrEdge = clr_edge;
    gl_Position = PM*VM*MM*vtx;
}
