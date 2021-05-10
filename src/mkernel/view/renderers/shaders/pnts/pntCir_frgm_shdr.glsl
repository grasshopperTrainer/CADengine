#version 450 core
// viewport size
layout (location = 4) uniform vec4 VPP; // viewport pixel property (posx, posy, width, height)

in vsOut {
    vec4 fclr;
    flat uvec3 goid;
    vec2 radVec;
    vec2 center;
    vec4 coord;
} vs_in;

layout (location = 0) out vec4 frag_clr;
layout (location = 1) out uvec4 goid;
layout (location = 2) out vec4 frag_coord;

float inf = 1.0/ 0.0;

void main() {
    goid = uvec4(vs_in.goid, 1);
    // fragment coordinated in NDC
    vec2 fc = ((gl_FragCoord.xy-VPP.xy)/VPP.zw-0.5)*2;
    // vector
    vec2 pntVec = fc - vs_in.center;
    // scale by screen ratio. z is measuring unit
    pntVec = pntVec*vec2(1, VPP.w/VPP.z);
    // vector is now scaled so simply check if point is outside radius
    if (length(pntVec) > vs_in.radVec.x) discard;
    frag_clr = vs_in.fclr;
    frag_coord = vec4(vs_in.coord.xyz, 1);
}
