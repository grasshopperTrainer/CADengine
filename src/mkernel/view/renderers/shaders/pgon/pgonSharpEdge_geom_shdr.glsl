#version 450 core

layout (lines_adjacency) in;
layout (triangle_strip, max_vertices = 4) out;

layout (location = 0) uniform mat4 PM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 MM = mat4(1.0);

in vsOut {
    float edgeThk;
    vec4 edgeClr;
    uint goid;
} vs_in[];


out vec4 edgeClr;
out uint goid;

vec4 vec_bisector(vec4 a, vec4 b) {
    // calculate bisector unit vector between two vectors
    vec4 bisector = (a+b)/2;
    return normalize(bisector);
}

vec4 pnt_offset(vec4 p, vec4 v, vec4 bi, float offset) {
    float amp = offset / length(cross(v.xyz, bi.xyz));
    return p + bi*amp;
}

void emit(vec4 p, mat4 tm, float zOff) {
    gl_Position = tm * p + vec4(0, 0, zOff, 0);
    EmitVertex();
}

void main() {
    mat4 TM = PM*VM*MM;
    float thk = vs_in[0].edgeThk/2;
    float zOff = -0.001;// closer to camera. prevent z fighting

    vec4 v10 = normalize(gl_in[0].gl_Position - gl_in[1].gl_Position);
    vec4 v12 = normalize(gl_in[2].gl_Position - gl_in[1].gl_Position);
    vec4 v23 = normalize(gl_in[3].gl_Position - gl_in[2].gl_Position);

    vec4 vb0 = vec_bisector(v10, v12);
    vec4 vb1 = vec_bisector(-v12, v23);

    vec4 a = pnt_offset(gl_in[1].gl_Position, v10, vb0, thk);
    vec4 b = pnt_offset(gl_in[1].gl_Position, v12, -vb0, thk);
    vec4 c = pnt_offset(gl_in[2].gl_Position, -v12, vb1, thk);
    vec4 d = pnt_offset(gl_in[2].gl_Position, v23, -vb1, thk);
    // need to determine coorect trapezoid
    if (dot(cross(v10.xyz, v12.xyz), cross(-v12.xyz, v23.xyz)) < 0) {
        vec4 t = c;
        c = d;
        d = t;
    }

    edgeClr = vs_in[0].edgeClr;
    goid = vs_in[0].goid;

    emit(a, TM, zOff);
    emit(b, TM, zOff);
    emit(c, TM, zOff);
    emit(d, TM, zOff);
    EndPrimitive();
}