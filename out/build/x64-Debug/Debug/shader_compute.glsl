#version 430 core
layout(local_size_x = 1, local_size_y = 1) in;
layout(rgba32f, binding = 0) uniform image2D imgOutput;

void main()
{
    ivec2 texelCoord = ivec2(gl_GlobalInvocationID.xy);
    vec4 color = vec4(
        float(texelCoord.x)/512.0,
        float(texelCoord.y)/512.0,
        0.5, 1.0
    );
    imageStore(imgOutput, texelCoord, color);
}
