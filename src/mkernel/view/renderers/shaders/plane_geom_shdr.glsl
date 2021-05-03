#version 450 core

layout (points) in;
layout (triangle_strip, max_vertices = 12) out;// three lines for axes

layout (location=0) uniform mat4 PM;
layout (location=1) uniform mat4 VM;
layout (location=2) uniform mat4 MM = mat4(1.0);

in vsOut {
    mat4 pln;
    float len;
    vec4 goid;
} vs_in[];

out vec4 fclr;
out vec4 foid;

// default colors
const vec4 origin = vs_in[0].pln[0];
const float thk = 0.01;
const mat4 TM = PM * VM * MM;
const vec4 clrs[3] = vec4[3](vec4(1, 0, 0, 1), vec4(0, 1, 0, 1), vec4(0, 0, 1, 1));
const vec4 vectors[3] = vec4[3](vs_in[0].pln[1], vs_in[0].pln[2], vs_in[0].pln[3]);


void emit_vertex(vec4 pos, vec4 clr) {
    fclr = clr;
    foid = vs_in[0].goid;

    gl_Position = TM * pos;
    EmitVertex();
}

void draw_axis(float scale, int i) {
    vec4 clr = clrs[i];

    // calculate offset normal
    vec3 norm = normalize(cross(vec3(0, 0, -1), (VM * MM * vectors[i]).xyz));
    vec4 off = inverse(VM * MM) * vec4(norm, 0) * thk * scale;
    vec4 end = origin + vectors[i] * scale;

    emit_vertex(origin + off, clr);
    emit_vertex(origin - off, clr);
    emit_vertex(end + off, clr);
    emit_vertex(end - off, clr);
    EndPrimitive();
}

void main() {
    // using camera distance for constant sizing
    // ambiguous length unit but leave it for now
    float scale = length(VM*MM*vs_in[0].pln[0])*vs_in[0].len;

    draw_axis(scale, 0);
    draw_axis(scale, 1);
    draw_axis(scale, 2);
}
