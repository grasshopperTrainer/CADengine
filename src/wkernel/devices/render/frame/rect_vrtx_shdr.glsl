#version 450 core

layout (location=0) in vec4 coord;
layout (location=1) in vec2 tex_coord;

layout (location=0) uniform mat4 PM;
layout (location=1) uniform mat4 VM;
layout (location=2) uniform mat4 MM;

out vec2 texCoord;

void main() {
    gl_Position = PM*VM*MM*coord;
    texCoord = tex_coord;
}
