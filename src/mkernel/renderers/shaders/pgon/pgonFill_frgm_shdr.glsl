#version 450

in vsOut {
    vec4 fclr;
    vec4 oid;
} vs_out;

layout(location = 0) out vec4 fclr;
layout(location = 1) out vec4 oid;

void main() {
    fclr = vs_out.fclr;
    oid = vs_out.oid;
}
