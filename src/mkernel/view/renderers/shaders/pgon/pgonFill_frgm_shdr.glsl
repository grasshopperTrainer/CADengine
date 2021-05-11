#version 450

in vsOut {
    vec4 clr;
    flat vec4 goid;
} fs_in;

layout(location = 0) out vec4 clr;
layout(location = 1) out vec4 goid;

void main() {
    clr = fs_in.clr;
    goid = fs_in.goid;
}
