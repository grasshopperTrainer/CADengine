#version 450 core

out vec4 fColor;

layout (location=0) uniform sampler2D myTexture;
layout (location=1) uniform sampler2D myDepth;

in vec2 texCoord;

void main() {
    fColor = texture(myTexture, texCoord);
    gl_FragDepth = texture(myDepth, texCoord).x;
}
