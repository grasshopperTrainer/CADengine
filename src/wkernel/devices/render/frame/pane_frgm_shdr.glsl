#version 450 core

out vec4 fColor;

layout (location=0) uniform sampler2D myTexture;

in vec2 texCoord;

void main() {
    fColor = texture(myTexture, texCoord);
}
