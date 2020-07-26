#version 330 core

layout (location = 0) in vec3 aVertex;

uniform mat4 model = mat4(
1,0,0,0,
0,1,0,0,
0,0,1,0,
0,0,0,1
);
uniform mat4 view = mat4(
1,0,0,0,
0,1,0,0,
0,0,1,0,
0,0,0,1
);
uniform mat4 projection = mat4(
1,0,0,0,
0,1,0,0,
0,0,1,0,
0,0,0,1
);

void main() {
    gl_Position = projection*view*model*vec4(aVertex, 1);
}
