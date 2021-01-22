#version 450 core

layout (location = 0) in vec4 vtx;
layout (location = 1) in vec4 clr;
layout (location = 2) in float dia;

layout (location = 0) uniform mat4 MM = mat4(1.0);
layout (location = 1) uniform mat4 VM = mat4(1.0);
layout (location = 2) uniform mat4 PM = mat4(1.0);
layout (location = 4) uniform vec2 VS;


out vec4 fclr;
out vec2 radVec;
out vec2 center;

void main() {
    fclr = clr;
    // camera space point
    vec4 csPnt = VM*MM*vtx;
    // radius vector at normalized device coordinate
    // ! PM will squach vector in relative with viewport ratio
    vec4 csRadVec = PM*vec4(dia/2, dia/2, csPnt.z, 0);
    // size from unit to pixel
    radVec = (csRadVec.xy/csRadVec.w)*VS;
    gl_PointSize = max(radVec.x, radVec.y);
    // size from pixel to ndc
    radVec = radVec/VS;
    // projection space point
    vec4 psPnt = PM*csPnt;

    center = psPnt.xy/psPnt.w;
    gl_Position = psPnt;
}
