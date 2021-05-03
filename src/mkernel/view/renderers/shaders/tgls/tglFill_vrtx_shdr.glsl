#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 3) in vec4 fill_clr;
layout (location = 4) in uint goid;

layout (location = 0) uniform mat4 PM;
layout (location = 1) uniform mat4 VM;
layout (location = 2) uniform mat4 MM = mat4(1.0);

out vec4 fclr;
out vec4 foid;
out vec4 fcoord;

void main() {
    fclr = fill_clr;
    fcoord = geo;
    foid = goid;
    gl_Position = PM*VM*MM*geo;
}