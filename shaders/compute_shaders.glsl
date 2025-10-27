#version 430

struct OrbitalElements {
    float a;
    float e;
    float i;
    float Omega;
    float omega;
    float M0;
};

layout(std430, binding = 0) buffer Asteroids {
    OrbitalElements asteroids[];
};

layout(std430, binding = 1) buffer Positions {
    vec4 positions[]; // x, y, z, w
};

uniform float t0; // days since epoch

vec3 propagateKepler(OrbitalElements orb, float t) {
    // Mean motion n
    float n = sqrt(1.0 / (orb.a * orb.a * orb.a)); // mu=1 AU^3/day^2
    float M = orb.M0 + n * t;

    // Keep M in 0..2pi
    M = mod(M, 6.2831853);

    // Solve Kepler's Equation iteratively
    float E = M;
    for(int k=0; k<5; k++)
        E = M + orb.e * sin(E);

    // Orbital plane coordinates
    float x_ = orb.a * (cos(E) - orb.e);
    float y_ = orb.a * sqrt(1.0 - orb.e * orb.e) * sin(E);

    // Rotate to 3D ecliptic
    float cosO = cos(orb.Omega), sinO = sin(orb.Omega);
    float cosw = cos(orb.omega), sinw = sin(orb.omega);
    float cosi = cos(orb.i), sini = sin(orb.i);

    vec3 pos;
    pos.x = (cosO*cosw - sinO*sinw*cosi)*x_ + (-cosO*sinw - sinO*cosw*cosi)*y_;
    pos.y = (sinO*cosw + cosO*sinw*cosi)*x_ + (-sinO*sinw + cosO*cosw*cosi)*y_;
    pos.z = (sinw*sini)*x_ + (cosw*sini)*y_;

    return pos;
}

layout(local_size_x = 1) in; // 1 asteroid for now

void main() {
    uint idx = gl_GlobalInvocationID.x;
    positions[idx] = vec4(propagateKepler(asteroids[idx], t0), 1.0);
}
