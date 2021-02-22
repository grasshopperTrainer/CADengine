#version 450 core

in vec4 clr;

layout(location=0) out vec4 frag_clr;
layout(location=1) out vec4 id_clr;
void main() {
    frag_clr = clr;
    id_clr = vec4(1, 0, 1, 1);
}
