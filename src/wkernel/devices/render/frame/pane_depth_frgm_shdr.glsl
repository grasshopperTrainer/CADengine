#version 450 core

layout (location=0) out vec4 clr;

layout (location=0) uniform sampler2D myTexture;
layout (location=1) uniform sampler2D myDepth;

in vec2 texCoord;

void main() {
    clr = texture(myTexture, texCoord);
    gl_FragDepth = texture(myDepth, texCoord).x;
}
