#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 3) in vec4 fill_clr;
layout (location = 4) in vec3 cid;

layout (location = 0) uniform mat4 PM;
layout (location = 1) uniform mat4 VM;
layout (location = 2) uniform mat4 MM = mat4(1.0);

out vec4 fclr;
out vec3 fcid;
out vec4 fcoord;

void main() {
    fclr = fill_clr;
    fcoord = vtx;
    fcid = cid;
    gl_Position = PM*VM*MM*vtx;
}
