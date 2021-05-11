#version 450 core

layout (lines) in;
layout (triangle_strip, max_vertices = 4) out;

layout (location = 0) uniform mat4 PM;
layout (location = 1) uniform mat4 VM;
layout (location = 2) uniform mat4 MM = mat4(1.0);

in vsOut {
    float thk;
    vec4 clr;
    vec4 goid;
} vs_in[];

out gsOut {
    vec4 clr;
    vec4 goid;
    vec4 coord;
} gs_out;

const mat4 VMM = VM * MM;
const mat4 IVMM = inverse(VMM);
const float hthk = vs_in[0].thk/2.0;

void emit_vertex(vec4 pos) {
    // invariants
    gs_out.clr = vs_in[0].clr;
    gs_out.goid = vs_in[0].goid;

    gs_out.coord = IVMM * pos;
    gl_Position = PM * pos;
    EmitVertex();
}

void main() {
    float thk = vs_in[0].thk;
    // transformed as so models are at position
    // with camera at origin and facing negetive z
    vec4 p0 = VMM*gl_in[0].gl_Position;
    vec4 p1 = VMM*gl_in[1].gl_Position;
    vec4 norm = vec4(normalize(cross(vec3(0, 0, -1), (p1 - p0).xyz)) * hthk, 0);
    // draw rect
    emit_vertex(p0 + norm);
    emit_vertex(p0 - norm);
    emit_vertex(p1 + norm);
    emit_vertex(p1 - norm);
    EndPrimitive();
}
