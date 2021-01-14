#version 430 core

layout (location = 0) in vec4 vtx;

uniform mat4 MM = mat4(1.0);
uniform mat4 VM = mat4(1.0);
uniform mat4 PM = mat4(1.0);

void main() {
    gl_Position = PM*VM*MM*vtx;
}
