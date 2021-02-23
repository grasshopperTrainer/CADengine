#version 450 core

in vec4 clr;
in vec3 cid;

layout(location=0) out vec4 frag_clr;
layout(location=1) out vec4 id_clr;

void main() {
    frag_clr = clr;
    id_clr = vec4(cid, 1);
}
