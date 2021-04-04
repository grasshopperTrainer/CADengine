#version 450

in vsOut {
    vec4 fclr;
    vec3 cid;
} vs_out;

layout(location = 0) out vec4 fclr;
layout(location = 1) out vec4 cid;

void main() {
    fclr = vs_out.fclr;
    cid = vec4(vs_out.cid, 1);
}
