#version 450 core

layout (points) in;
layout (triangle_strip, max_vertices = 3) out;

layout (location = 0) uniform mat4 MM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 PM = mat4(1.0);

in vsOut {
    vec3 cid;
    vec4 clr;
    float dia;
} vs_in[];

out gsOut {
    vec3 cid;
    vec4 clr;
} gs_out;

void main() {
    gs_out.cid = vs_in[0].cid;
    // invariants
    gs_out.clr = vs_in[0].clr;
    float rad = vs_in[0].dia/2;  //circumcircle
    float cosv = cos(radians(120));
    float sinv = sin(radians(120));
    // transposed
    mat4 rotMat = mat4(
    cosv, sinv, 0, 0,
    -sinv, cosv, 0, 0,
    0, 0, 1, 0,
    0, 0, 0, 1);
    vec4 pnt = VM*MM*gl_in[0].gl_Position;
    // vectors of identical size
    vec4 vec = vec4(0, rad, 0, 0);
    // move and apply projection matrix to finish transformation
    // draw triangle up
    gl_Position = PM*(pnt + vec);
    EmitVertex();
    // left
    vec = rotMat*vec;
    gl_Position = PM*(pnt + vec);
    EmitVertex();
    // right
    vec = rotMat*vec;
    gl_Position = PM*(pnt + vec);
    EmitVertex();
    EndPrimitive();
}
