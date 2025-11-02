#version 430 core

layout(std430, binding = 0) buffer OrbitalElementsBuffer {
    float a[];
    float e[];
    float i[];
    float Omega[];
    float omega[];
    float M0[];
};

layout(std430, binding = 1) buffer PositionBuffer {
    vec4 pos[];
};

uniform float t0;

void main() {
    uint id = gl_GlobalInvocationID.x;
    // Dummy position calculation � just a placeholder
    float x = a[id] * cos(M0[id] + t0 * 0.001);
    float y = a[id] * sin(M0[id] + t0 * 0.001);
    float z = 0.0;
    pos[id] = vec4(x, y, z, 1.0);
}
