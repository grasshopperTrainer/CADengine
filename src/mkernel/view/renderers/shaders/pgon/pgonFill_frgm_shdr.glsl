#version 450

in vsOut {
    vec4 fclr;
    flat uint goid;
} vs_out;

layout(location = 0) out vec4 fclr;
layout(location = 1) out uint goid;

void main() {
    fclr = vs_out.fclr;
    goid = vs_out.goid;
}
