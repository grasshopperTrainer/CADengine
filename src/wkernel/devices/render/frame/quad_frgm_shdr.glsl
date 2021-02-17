#version 450 core

out vec4 fColor;

uniform sampler2D myTexture;

in vec2 texCoord;

void main() {
    fColor = texture(myTexture, texCoord);
}
