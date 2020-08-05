#version 330 core

layout (location = 0) in vec3 aVertex;

uniform mat4 MM = mat4(1.0);
uniform mat4 VM = mat4(1.0);
uniform mat4 PM = mat4(1.0);

void main() {
    gl_Position = PM*VM*MM*vec4(aVertex, 1);
}
