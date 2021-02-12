#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 3) in vec4 fill_clr;

layout (location = 0) uniform mat4 MM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 PM = mat4(1.0);

out vec4 fFillClr;

void main() {
    fFillClr = fill_clr;
    gl_Position = PM*VM*MM*vtx;
}
