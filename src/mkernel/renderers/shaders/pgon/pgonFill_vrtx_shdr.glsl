#version 450

layout(location = 0) in vec4 vtx;
layout(location = 1) in float edge_thk;
layout(location = 2) in vec4 clr_edge;
layout(location = 3) in vec4 clr_fill;

layout(location = 0) uniform mat4 PM;
layout(location = 1) uniform mat4 VM;
layout(location = 2) uniform mat4 MM;

out vec4 fclr;

void main() {
    fclr = clr_fill;
    gl_Position = PM*VM*MM*vtx;
}
