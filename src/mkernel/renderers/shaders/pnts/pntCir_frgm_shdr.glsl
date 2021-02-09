#version 450 core
// viewport size
layout (location = 4) uniform vec4 VPP; // viewport pixel property (posx, posy, width, height)

in vec4 fclr;
in vec2 radVec;
in vec2 center;

out vec4 FragColor;

void main() {
    // fragment coordinated in NDC

    vec2 fc = ((gl_FragCoord.xy-VPP.xy)/VPP.zw-0.5)*2;
    // vector
    vec2 pntVec = fc - center;
    // scale by screen ratio. z is measuring unit
    pntVec = pntVec*vec2(1, VPP.w/VPP.z);
    // vector is now scaled so simply check if point is outside radius
    if (length(pntVec) > radVec.x) discard;
    FragColor = fclr;
}
