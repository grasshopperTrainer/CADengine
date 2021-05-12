#version 450 core

in gsOut {
    vec4 clr;
    vec4 coord;
    flat vec4 goid;
} fs_in;

layout(location=0) out vec4 fclr;
layout(location=1) out vec4 goid;
layout(location=2) out vec4 fcoord;

void main() {
    fclr = fs_in.clr;
    goid = fs_in.goid;
    fcoord = fs_in.coord;
}
