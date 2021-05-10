#version 450 core

in gsOut {
    vec4 clr;
    vec4 coord;
    flat uvec3 goid;
} fs_in;

layout(location=0) out vec4 fclr;
layout(location=1) out uvec4 goid;
layout(location=2) out vec4 fcoord;

void main() {
    fclr = fs_in.clr;
    goid = uvec4(fs_in.goid, 1);
    fcoord = fs_in.coord;
}
