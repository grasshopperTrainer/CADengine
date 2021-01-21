#version 450 core

layout (lines) in;
layout (triangle_strip, max_vertices = 4) out;

layout (location = 0) uniform mat4 MM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 PM = mat4(1.0);

in vsOut {
    float thk;
    vec4 clr;
} vs_in[];

out vec4 clr;

void main() {
    // invariants
    clr = vs_in[0].clr;
    float thk = vs_in[0].thk;
    // transformed as so models are at position
    // with camera at origin and facing negetive z
    vec3 p0 = (VM*MM*gl_in[0].gl_Position).xyz;
    vec3 p1 = (VM*MM*gl_in[1].gl_Position).xyz;
    // line vector crossed with camera pointing yields perpendicular to nv
    vec3 perp = cross(p1 - p0, vec3(0, 0, -1));
    // amplify to correct thikness
    perp = normalize(perp) * (thk/2);
    // move and apply projection matrix to finish transformation
    // draw rect
    gl_Position = PM*vec4(p0 + perp, 1);
    EmitVertex();
    gl_Position = PM*vec4(p0 - perp, 1);
    EmitVertex();
    gl_Position = PM*vec4(p1 + perp, 1);
    EmitVertex();
    gl_Position = PM*vec4(p1 - perp, 1);
    EmitVertex();
    EndPrimitive();
}
