#version 430 core

out vec4 FragColor;

uniform vec4 color = vec4(1,1,0,1);

void main() {
    FragColor = color;
}
