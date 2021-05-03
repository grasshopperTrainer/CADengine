#version 450

in vsOut {
    vec4 fclr;
    vec4 goid;
} vs_out;

layout(location = 0) out vec4 fclr;
layout(location = 1) out vec4 goid;

void main() {
    fclr = vs_out.fclr;
    goid = vs_out.goid;
}
