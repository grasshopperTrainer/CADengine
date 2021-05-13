#version 450 core

layout (points) in;
layout (triangle_strip, max_vertices = 4) out;

// camera plane coordinates and render pos
layout (location=6) uniform mat4 fn_coord;
layout (location=7) uniform mat4 ff_coord;

// match vertex order
const vec2 pos[] = {vec2(-1, -1), vec2(1, -1), vec2(-1, 1), vec2(1, 1)};
const vec4 fn_coords[] = {fn_coord[0], fn_coord[1], fn_coord[3], fn_coord[2]};
const vec4 ff_coords[] = {ff_coord[0], ff_coord[1], ff_coord[3], ff_coord[2]};

in vsAttr {
    vec3 ori;
    vec3 dir;
    float thk;
    vec3 goid;
} gs_in[];

out gsAttr {
    vec3 ori;
    vec3 dir;
    float thk;
    vec3 goid;

    // ndc coordinat, frustum near, far plane coord
    vec3 ndc_coord;
    vec3 fn_coord;
    vec3 ff_coord;
} gs_out;

void emit(int i) {
    gs_out.ndc_coord = vec3(pos[i], -1);
    gs_out.fn_coord = fn_coords[i].xyz;
    gs_out.ff_coord = ff_coords[i].xyz;

    gl_Position = vec4(pos[i], -1, 1);
    EmitVertex();
}

void main() {
    gs_out.ori = gs_in[0].ori;
    gs_out.dir = gs_in[0].dir;
    gs_out.thk= gs_in[0].thk;
    gs_out.goid = gs_in[0].goid;

    for(int i=0; i<4; i++) {
        emit(i);
    }
    EndPrimitive();
}
