#include <glew.h>
#include <glfw3.h>
// #include <GLFW/glfw3.h>
#include <json.hpp>
#include "shader.h"
#include <iostream>
#include <fstream>
#include <vector>
#include <cmath>
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

struct OrbitalElements { float a, e, i, Omega, omega, M0; };
struct Position { float x, y, z, w; };

OrbitalElements readAsteroidJSON(const std::string& filename) {
    OrbitalElements orb{};
    std::ifstream file(filename);
    nlohmann::json j; file >> j;

    for (auto& el : j["orbit"]["elements"]) {
        std::string name = el["name"];
        float value = std::stof(el["value"].get<std::string>());
        if (name == "a") orb.a = value;
        else if (name == "e") orb.e = value;
        else if (name == "i") orb.i = value * M_PI / 180.0f;
        else if (name == "om") orb.Omega = value * M_PI / 180.0f;
        else if (name == "w") orb.omega = value * M_PI / 180.0f;
        else if (name == "ma") orb.M0 = value * M_PI / 180.0f;
    }
    return orb;
}

int main() {
    if (!glfwInit()) { std::cerr << "GLFW init failed\n"; return -1; }
    GLFWwindow* window = glfwCreateWindow(100, 100, "", NULL, NULL);
    glfwMakeContextCurrent(window);
    glewInit();

    OrbitalElements ceres = readAsteroidJSON("data/1_Ceres.json");
    std::vector<OrbitalElements> asteroids{ ceres };
    std::vector<Position> positions(1);

    // SSBO for orbital elements
    GLuint ssbo;
    glGenBuffers(1, &ssbo);
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo);
    glBufferData(GL_SHADER_STORAGE_BUFFER, asteroids.size() * sizeof(OrbitalElements), asteroids.data(), GL_STATIC_DRAW);
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, ssbo);

    // SSBO for positions
    GLuint posSSBO;
    glGenBuffers(1, &posSSBO);
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, posSSBO);
    glBufferData(GL_SHADER_STORAGE_BUFFER, positions.size() * sizeof(Position), nullptr, GL_DYNAMIC_DRAW);
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, posSSBO);

    GLuint computeShader = loadComputeShader("shaders/compute_shader.glsl");
    glUseProgram(computeShader);

    float t0 = 2025.0f - 2021.0f; // days since epoch or you can compute JD diff
    glUniform1f(glGetUniformLocation(computeShader, "t0"), t0);

    glDispatchCompute(1, 1, 1);
    glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT);

    glBindBuffer(GL_SHADER_STORAGE_BUFFER, posSSBO);
    Position* ptr = (Position*)glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY);
    std::cout << "1_Ceres Position: x=" << ptr[0].x << " y=" << ptr[0].y << " z=" << ptr[0].z << "\n";
    glUnmapBuffer(GL_SHADER_STORAGE_BUFFER);

    glfwTerminate();
    return 0;
}
