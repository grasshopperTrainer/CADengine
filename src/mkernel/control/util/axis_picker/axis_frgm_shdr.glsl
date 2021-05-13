#version 450 core

layout (location=1) out vec4 goid;
layout (location=2) out vec4 coord;

layout (location=0) uniform mat4 PM;
layout (location=1) uniform mat4 VM;
layout (location=2) uniform vec2 pane_size;
layout (location=3) uniform vec4 LRBT;// near frustum dim
layout (location=4) uniform float cam_near;
layout (location=5) uniform vec4 cam_ori;

in gsAttr {
    vec3 ori;
    vec3 dir;
    float thk;
    vec3 goid;

    // ndc coordinat, frustum near, far plane coord
    vec3 ndc_coord;
    vec3 fn_coord;
    vec3 ff_coord;
} fs_in;

vec3 intx_ray_pln(vec3 rori, vec3 rvec, vec3 pori, vec3 pnorm) {
    float t = dot(pnorm, pori - rori) / dot(pnorm, rvec);
    return rori + t * rvec;
}

vec3 intx_ray_pnt(vec3 rori, vec3 rvec, vec3 pnt) {
    float t = dot(rvec, pnt - rori);
    return rori + t * rvec;
}
vec3 intx_ray_ray(vec3 aOri, vec3 aVec, vec3 bOri, vec3 bVec) {
    vec3 cVec = bOri - aOri;
    vec3 v0 = cross(aVec, bVec);
    vec3 v1 = cross(cVec, bVec);

    float t = dot(v1, v0) / pow(length(v0), 2);
    vec3 I = aOri + aVec * t;
    return I;
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

    // view space ray reference points
    vec3 p0 = (VM * vec4(fs_in.ori, 1)).xyz;
    vec3 p1 = (VM * vec4(fs_in.ori + fs_in.dir, 1)).xyz;

    // ray vec on flat camera near plane
    vec3 flat_p0 = intx_ray_pln(eye, p0-eye, vec3(0, 0, -cam_near), vec3(0, 0, 1));
    vec3 flat_p1 = intx_ray_pln(eye, p1-eye, vec3(0, 0, -cam_near), vec3(0, 0, 1));
    vec3 flat_dir = normalize(flat_p1 - flat_p0);

    // scale frustum near and pixel coordinates
    float width = LRBT.y - LRBT.x;
    float height = LRBT.w - LRBT.z;
    vec3 frustum_ori = vec3((LRBT.x + LRBT.y)/2, (LRBT.z + LRBT.w)/2, -cam_near);
    mat4 SM = scale_mat(width/2, height/2, 1);// scale up to given near plane size
    mat4 MM = move_mat(frustum_ori.x, frustum_ori.y, -frustum_ori.z);// move if frustum not centered
    vec4 flat_pixel_coord = MM * SM * vec4(fs_in.ndc_coord, 1);

    // calculate distance between ray and pixel
    vec2 I = (intx_ray_pnt(vec3(flat_p0.xy, 0), flat_dir, flat_pixel_coord.xyz)).xy;
    float d = distance(I, flat_pixel_coord.xy);

    //     find half thickness
    float ht = fs_in.thk * width/(pane_size.x*2);

    // render result
    if (d < ht) {
        goid = vec4(fs_in.goid, 1);
        vec3 cam_ray = normalize(fs_in.ff_coord - fs_in.fn_coord);
        vec3 k = intx_ray_ray(fs_in.ori, fs_in.dir, cam_ori.xyz, cam_ray);
        coord = vec4(k, 1);
    } else {
        discard;
    }
    //    gl_FragDepth = 0.45;
}
