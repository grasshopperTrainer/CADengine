#version 450

layout(location = 0) in vec4 geo;
layout(location = 1) in float edge_thk;
layout(location = 2) in vec4 clr_edge;
layout(location = 3) in vec4 clr_fill;
layout(location = 4) in vec3 goid;
layout(location = 5) in int goid_flag;

layout(location = 0) uniform mat4 PM;
layout(location = 1) uniform mat4 VM;
layout(location = 2) uniform mat4 MM;

out vsOut {
    vec4 clr;
    vec4 goid;
} vs_out;

void main() {
    vs_out.clr = clr_fill;
    vs_out.goid = vec4(goid, goid_flag);

    gl_Position = PM*VM*MM*geo;
}
