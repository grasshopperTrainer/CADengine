#version 450 core

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

layout (location = 0) uniform mat4 MM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 PM = mat4(1.0);

in vsOut {
    vec4 clr;
    float dia;
    uvec3 goid;
} gs_in[];

out gsOut {
    vec4 clr;
    vec4 coord;
    uvec3 goid;
} gs_out;

const mat4 VMM = VM * MM;
const mat4 IVMM = inverse(VMM);

void emit_vertex(vec4 pos) {
    gs_out.coord = IVMM * pos;
    gl_Position = PM*pos;
    EmitVertex();
}

void main() {
    // invariants
    gs_out.clr = gs_in[0].clr;
    gs_out.goid = gs_in[0].goid;
    float rad = gs_in[0].dia/2;
    vec4 pnt = VMM*gl_in[0].gl_Position;
    // vectors of identical size
    vec4 movex = vec4(1, 0, 0, 0) * rad;
    vec4 movey = vec4(0, 1, 0, 0) * rad;
    // move and apply projection matrix to finish transformation
    // draw rect
    emit_vertex(pnt - movex + movey);
    emit_vertex(pnt - movex - movey);
    emit_vertex(pnt + movex + movey);
    emit_vertex(pnt + movex - movey);
    EndPrimitive();
}
