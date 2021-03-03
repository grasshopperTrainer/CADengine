#version 450 core

layout (points) in;
layout (line_strip, max_vertices = 18) out;// three lines for axes

layout (location=0) uniform mat4 PM;
layout (location=1) uniform mat4 VM;
layout (location=2) uniform mat4 MM = mat4(1.0);

in vsOut {
    mat4 pln;
    float len;
} vs_in[];

out vec4 clr;

// default colors
const vec4 origin = vs_in[0].pln[0];
const mat4 TM = PM * VM * MM;
const vec4 clrs[3] = vec4[3](vec4(1, 0, 0, 1), vec4(0, 1, 0, 1), vec4(0, 0, 1, 1));
const vec4 vectors[3] = vec4[3](vs_in[0].pln[1], vs_in[0].pln[2], vs_in[0].pln[3]);

void draw_axis(float scale, int i) {
    clr = clrs[i];

    mat2x4 vertices = mat2x4(origin, vs_in[0].pln[0] + vectors[i] * scale);
    gl_Position = TM * vertices[0];
    EmitVertex();
    gl_Position = TM * vertices[1];
    EmitVertex();
    EndPrimitive();

    mat4 MoveM = mat4(1.0);
    MoveM[3] = vectors[(i+1)%3] * scale * 0.005;
    MoveM[3][3] = 1;

    gl_Position = TM * MoveM * vertices[0];
    EmitVertex();
    gl_Position = TM * MoveM * vertices[1];
    EmitVertex();
    EndPrimitive();

    MoveM[3] = vectors[(i+1)%3] * scale * -0.005;
    MoveM[3][3] = 1;

    gl_Position = TM * MoveM * vertices[0];
    EmitVertex();
    gl_Position = TM * MoveM * vertices[1];
    EmitVertex();
    EndPrimitive();
}

void main() {
    // using camera distance for constant sizing
    // ambiguous length unit but leave it for now
    float scale = length(VM*MM*vs_in[0].pln[0])*vs_in[0].len;
    vec4 origin = PM * VM * MM * vs_in[0].pln[0];

    draw_axis(scale, 0);
    draw_axis(scale, 1);
    draw_axis(scale, 2);
}
