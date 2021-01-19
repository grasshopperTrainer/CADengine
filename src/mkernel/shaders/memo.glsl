#version 120

void main() {

}

vec3 vec_pnts(vec3 a, vec3 b) {
    return b - a;
}

vec3 vec_perp(vec3 obj, vec3 hint) {
    // find perpendicular vector of obj, with a help of hint vector
    return cross(obj, cross(hint, obj));
}

vec3 pnt_move(vec3 p, vec3 v) {
    // move point by given vector
    return p + v;
}

vec3 vec_bisector(vec3 a, vec3 b) {
    // calculate bisector unit vector between two vectors
    vec3 bisector = (normalize(a)+normalize(b))/2;
    return normalize(bisector);
}

float angle_between(vec3 a, vec3 b) {
    // calculate angle between two vectors in domain(0, 1)
    return acos(dot(a, b) / length(a) * length(b));
}
