#version 450 core

layout (triangles) in;
layout (triangle_strip, max_vertices = 8) out;

layout (location = 0) uniform mat4 PM;
layout (location = 1) uniform mat4 VM;
layout (location = 2) uniform mat4 MM = mat4(1.0);

in vsOut {
    float edgeThk;
    vec4 edgeClr;
    vec3 cid;
} vs_in[];

out vec4 edgeClr;
out vec3 fcid;
out vec4 fcoord;

const mat4 TM = PM * VM * MM;

vec3 vec_pnts(vec3 a, vec3 b) {
    return b - a;
}

vec3 vec_bisector(vec3 a, vec3 b) {
    // calculate bisector unit vector between two vectors
    vec3 bisector = (a+b)/2;
    return normalize(bisector);
}

vec3 pnt_offset(vec3 p, vec3 v0, vec3 v1, float offset) {
    vec3 bi = vec_bisector(v0, v1);
    float amp = offset / length(cross(v0, bi));
    return p + bi*amp;
}

void emit(vec3 p, float zOff) {
    vec4 pos = vec4(p, 1) + vec4(0, 0, zOff, 0);
    fcoord = pos;
    gl_Position = TM * pos;
    EmitVertex();
}

void main() {
    mat4 trnsf_mat = PM*VM*MM;
    float thk = vs_in[0].edgeThk/2;
    float zOff = -0.001;   // closer to camera. prevent z fighting

    vec3 p0 = gl_in[0].gl_Position.xyz;
    vec3 p1 = gl_in[1].gl_Position.xyz;
    vec3 p2 = gl_in[2].gl_Position.xyz;

    vec3 v01 = normalize(vec_pnts(p0, p1));
    vec3 v02 = normalize(vec_pnts(p0, p2));
    vec3 v12 = normalize(vec_pnts(p1, p2));

    vec3 inner0 = pnt_offset(p0, v01, v02, thk);
    vec3 inner1 = pnt_offset(p1, v12, -v01, thk);
    vec3 inner2 = pnt_offset(p2, -v02, -v12, thk);
    vec3 outer0 = pnt_offset(p0, v01, v02, -thk);
    vec3 outer1 = pnt_offset(p1, v12, -v01, -thk);
    vec3 outer2 = pnt_offset(p2, -v02, -v12, -thk);

    fcid = vs_in[0].cid;
    edgeClr = vs_in[0].edgeClr;
    emit(inner0, zOff);
    emit(outer0, zOff);
    emit(inner1, zOff);
    emit(outer1, zOff);
    emit(inner2, zOff);
    emit(outer2, zOff);
    emit(inner0, zOff);
    emit(outer0, zOff);
    EndPrimitive();
}