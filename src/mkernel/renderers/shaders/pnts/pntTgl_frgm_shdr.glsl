#version 450 core

in gsOut {
    vec3 cid;
    vec4 clr;
} gs_in;

layout (location=0) out vec4 fclr;
layout (location=1) out vec4 cid;

void main() {
    fclr = gs_in.clr;
    cid = vec4(gs_in.cid, 1);
}
