#version 430 core

layout (location = 1) in vec4 color;

out vec4 FragColor;

void main() {
    FragColor = color;
}
