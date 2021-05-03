#version 450 core

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

layout (location = 0) uniform mat4 MM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 PM = mat4(1.0);

in vsOut {
    vec4 clr;
    float dia;
    uint goid;
} vs_in[];

out vec4 clr;
out uint goid;
out vec4 coord;

const mat4 VMM = VM * MM;
const mat4 IVMM = inverse(VMM);

void emit_vertex(vec4 pos) {
    coord = IVMM * pos;
    gl_Position = PM*pos;
    EmitVertex();
}

void main() {
    // invariants
    clr = vs_in[0].clr;
    goid = vs_in[0].goid;
    float rad = vs_in[0].dia/2;
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
