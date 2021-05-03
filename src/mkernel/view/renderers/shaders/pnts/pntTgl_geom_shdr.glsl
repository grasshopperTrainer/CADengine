#version 450 core

layout (points) in;
layout (triangle_strip, max_vertices = 3) out;

layout (location = 0) uniform mat4 MM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 PM = mat4(1.0);

in vsOut {
    vec4 goid;
    vec4 clr;
    float dia;
} vs_in[];

out gsOut {
    vec4 goid;
    vec4 clr;
    vec4 coord;
} gs_out;

const mat4 VMM = VM * MM;
const mat4 IVMM = inverse(VMM);

void emit_vertex(vec4 pos) {
    gs_out.coord = IVMM * pos;
    gl_Position = PM*pos;
    EmitVertex();
}

void main() {
    gs_out.goid = vs_in[0].goid;
    // invariants
    gs_out.clr = vs_in[0].clr;
    float rad = vs_in[0].dia/2;//circumcircle
    float cosv = cos(radians(120));
    float sinv = sin(radians(120));
    // transposed
    mat4 rotMat = mat4(
    cosv, sinv, 0, 0,
    -sinv, cosv, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1);
    vec4 pnt = VMM*gl_in[0].gl_Position;
    // vectors of identical size
    vec4 vec = vec4(0, rad, 0, 0);
    // move and apply projection matrix to finish transformation
    emit_vertex(pnt + vec);// up
    emit_vertex(pnt + rotMat*vec);// left
    emit_vertex(pnt + inverse(rotMat)*vec);// right
    EndPrimitive();
}
