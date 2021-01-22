#version 450 core

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

layout (location = 0) uniform mat4 MM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 PM = mat4(1.0);

in vsOut {
    vec4 clr;
    float dia;
} vs_in[];

out vec4 clr;

void main() {
    // invariants
    clr = vs_in[0].clr;
    float rad = vs_in[0].dia/2;
    vec4 pnt = VM*MM*gl_in[0].gl_Position;
    // vectors of identical size
    vec4 movex = vec4(1, 0, 0, 0) * rad;
    vec4 movey = vec4(0, 1, 0, 0) * rad;
    // move and apply projection matrix to finish transformation
    // draw rect
    gl_Position = PM*(pnt - movex + movey);
    EmitVertex();
    gl_Position = PM*(pnt - movex - movey);
    EmitVertex();
    gl_Position = PM*(pnt + movex + movey);
    EmitVertex();
    gl_Position = PM*(pnt + movex - movey);
    EmitVertex();
    EndPrimitive();
}
