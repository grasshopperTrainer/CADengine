#version 450 core

layout (location=1) out vec4 cid;

layout (location=0) uniform mat4 PM;
layout (location=1) uniform mat4 VM;
layout (location=2) uniform float near;
layout (location=3) uniform vec4 cam_ori;
layout (location=4) uniform vec4 LRBT; // texture size

in vsAttr {
    vec3 ori;
    vec3 dir;
    vec3 ncoord;
    vec3 fcoord;
    vec3 coord;
    float thk;
    vec3 cid;
} fs_in;


const vec3 cori = cam_ori.xyz;

vec3 intx_ray_pln(vec3 rori, vec3 rvec, vec3 pori, vec3 pnorm) {
    float t = dot(pnorm, pori - rori) / dot(pnorm, rvec);
    return rori + t * rvec;
}

vec3 intx_ray_pnt(vec3 rori, vec3 rvec, vec3 pnt) {
    float t = dot(rvec, pnt - rori);
    return rori + t * rvec;
}

mat4 scale_mat(float x, float y, float z) {
    mat4 M = mat4(
                vec4(x, 0, 0, 0),
                vec4(0, y, 0, 0),
                vec4(0, 0, z, 0),
                vec4(0, 0, 0, 1)
            );
    return M;
}

mat4 move_mat(float x, float y, float z) {
    mat4 M = mat4(
                vec4(1, 0, 0, 0),
                vec4(0, 1, 0, 0),
                vec4(0, 0, 1, 0),
                vec4(x, y, z, 1)
            );
    return M;
}

void main() {
    vec3 eye = vec3(0, 0, 0);
    // pixel ray
    vec3 pixel_ray = normalize(fs_in.fcoord - fs_in.ncoord);

    // view space ray
    vec3 p0 = (VM * vec4(fs_in.ori, 1)).xyz;
    vec3 p1 = (VM * vec4(fs_in.ori+fs_in.dir, 1)).xyz;

    // flat ray vec
    vec3 flat_p0 = intx_ray_pln(eye, p0-eye, vec3(0, 0, -near), vec3(0, 0, 1));
    vec3 flat_p1 = intx_ray_pln(eye, p1-eye, vec3(0, 0, -near), vec3(0, 0, 1));
    vec3 flat_dir = normalize(flat_p1 - flat_p0);

    // scale frustum near plane to match NDC near plane
    mat4 SM = scale_mat(2/(LRBT.y - LRBT.x), 2/(LRBT.w - LRBT.z), 1); // scale up to given near plane size
    mat4 MM = move_mat((LRBT.y + LRBT.x)/2, (LRBT.w + LRBT.z)/2, -near); // move if needed
    vec2 norm_flat_p0 = (SM * vec4(flat_p0.xy, 0, 1)).xy;

    // calculate distance between ray and pixel
    vec2 I = (intx_ray_pnt(vec3(norm_flat_p0, 0), flat_dir, fs_in.coord.xyz)).xy;
    float d = distance(I, fs_in.coord.xy);

    // find half thickness
//    float ht =

    // render result
    if (d < 0.01) {
        cid = vec4(fs_in.cid, 1);
    } else {
        discard;
    }
        //    gl_FragDepth = 0.45;
}
