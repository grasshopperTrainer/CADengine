#version 450 core

layout (location = 0) in vec4 geo;
layout (location = 3) in vec4 fill_clr;
layout (location = 4) in vec3 goid;
layout (location = 5) in int goid_flag;

layout (location = 0) uniform mat4 PM;
layout (location = 1) uniform mat4 VM;
layout (location = 2) uniform mat4 MM = mat4(1.0);

out vsOut {
    vec4 clr;
    vec4 goid;
    vec4 coord;
} vs_out;

void main() {
    vs_out.clr = fill_clr;
    vs_out.coord = geo;
    vs_out.goid = vec4(goid, goid_flag);
    gl_Position = PM*VM*MM*geo;
}
