//#include <iostream>
//#include <fstream>
//#include <vector>
//#include <string>
//#include <cmath>
//#include <filesystem>
//
//#include <GL/glew.h>
//#include <GLFW/glfw3.h>
//#include <nlohmann/json.hpp>
//
//#include "main_functions.h"
//
//using json = nlohmann::json;
//namespace fs = std::filesystem;
//
//const unsigned int LOCAL_SIZE_X = 256;
//const std::string DATA_DIR = "data";
//
//struct Position { float x, y, z, w; };
//
//// ===================== COMPUTE SHADER =====================
//const char* computeShaderSrc = R"(
//#version 430 core
//layout(local_size_x = 256) in;
//
//struct OrbitalElements {
//    float a;
//    float e;
//    float i;
//    float Omega;
//    float omega;
//    float M0;
//};
//
//layout(std430, binding = 0) readonly buffer OrbElements {
//    OrbitalElements elements[];
//};
//
//layout(std430, binding = 1) writeonly buffer Positions {
//    vec4 pos[];
//};
//
//uniform float t_days;
//const float TWO_PI = 6.28318530717958647692;
//
//float solveE(float M, float e) {
//    float E = M;
//    if (E > 3.14159265) E -= TWO_PI;
//    for (int k = 0; k < 20; ++k) {
//        float f = E - e * sin(E) - M;
//        float df = 1.0 - e * cos(E);
//        float dE = -f / df;
//        E += dE;
//        if (abs(dE) < 1e-7) break;
//    }
//    return E;
//}
//
//void main() {
//    uint gid = gl_GlobalInvocationID.x;
//    OrbitalElements oe = elements[gid];
//
//    const float k = 0.01720209895;
//    float n = k / pow(oe.a, 1.5);
//    float M = mod(oe.M0 + n * t_days, TWO_PI);
//    float E = solveE(M, oe.e);
//
//    float cosE = cos(E), sinE = sin(E);
//    float x_orb = oe.a * (cosE - oe.e);
//    float y_orb = oe.a * sqrt(max(0.0, 1.0 - oe.e * oe.e)) * sinE;
//
//    float cosO = cos(oe.Omega), sinO = sin(oe.Omega);
//    float cosw = cos(oe.omega), sinw = sin(oe.omega);
//    float cosi = cos(oe.i), sini = sin(oe.i);
//
//    float x = (cosO*cosw - sinO*sinw*cosi)*x_orb +
//              (-cosO*sinw - sinO*cosw*cosi)*y_orb;
//    float y = (sinO*cosw + cosO*sinw*cosi)*x_orb +
//              (-sinO*sinw + cosO*cosw*cosi)*y_orb;
//    float z = (sinw*sini)*x_orb + (cosw*sini)*y_orb;
//
//    pos[gid] = vec4(x, y, z, 1.0);
//}
//)";
//
//// ===================== MAIN =====================
//int main() {
//
//    // --- Headless OpenGL ---
//    if (!glfwInit()) return -1;
//    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
//    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
//    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
//    glfwWindowHint(GLFW_VISIBLE, GLFW_FALSE);
//
//    GLFWwindow* window =
//        glfwCreateWindow(1, 1, "manual", nullptr, nullptr);
//    if (!window) return -1;
//
//    glfwMakeContextCurrent(window);
//    glewExperimental = GL_TRUE;
//    if (glewInit() != GLEW_OK) return -1;
//
//    // ---------- Read targets ----------
//    std::vector<std::string> targets;
//    std::ifstream tf("C:/Users/JASMINE/Desktop/RnD_asteroid/targets_english.txt");
//
//    std::string s;
//    while (std::getline(tf, s)) {
//        if (!s.empty()) {
//            for (char& c : s)
//                if (c == ' ') c = '_';
//            targets.push_back(s + ".json");
//        }
//    }
//
//    // ---------- Load orbital elements ----------
//    std::vector<OrbitalElements> elements;
//    for (auto& t : targets) {
//        OrbitalElements oe{};
//        if (readOrbitalElementsFromJSON(fs::path(DATA_DIR) / t, oe))
//            elements.push_back(oe);
//    }
//
//    if (elements.empty()) {
//        std::cerr << "No orbital data loaded\n";
//        return -1;
//    }
//
//    size_t N = elements.size();
//    std::cout << "[INFO] Loaded " << N << " asteroids\n";
//
//    // ---------- Output directory ----------
//    fs::path outDir =
//        "C:/Users/JASMINE/Desktop/RnD_asteroid/results/manual";
//    fs::create_directories(outDir);
//
//    // ---------- GPU ----------
//    GLuint ssboElems, ssboPos;
//    glGenBuffers(1, &ssboElems);
//    glGenBuffers(1, &ssboPos);
//
//    GLuint cs = compileShader(GL_COMPUTE_SHADER, computeShaderSrc);
//    GLuint prog = glCreateProgram();
//    glAttachShader(prog, cs);
//    glLinkProgram(prog);
//    glUseProgram(prog);
//
//    GLint loc_t = glGetUniformLocation(prog, "t_days");
//
//    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssboElems);
//    glBufferData(GL_SHADER_STORAGE_BUFFER,
//        sizeof(OrbitalElements) * N,
//        elements.data(), GL_STATIC_DRAW);
//    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, ssboElems);
//
//    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssboPos);
//    glBufferData(GL_SHADER_STORAGE_BUFFER,
//        sizeof(Position) * N, nullptr, GL_DYNAMIC_COPY);
//    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, ssboPos);
//
//    GLuint groups = (GLuint)((N + LOCAL_SIZE_X - 1) / LOCAL_SIZE_X);
//
//    // ---------- CSV files ----------
//    std::vector<std::ofstream> csv(N);
//    for (size_t i = 0; i < N; ++i) {
//        std::string name =
//            targets[i].substr(0, targets[i].find('.')) + ".csv";
//        csv[i].open(outDir / name, std::ios::trunc);
//        csv[i] << "date,x,y,z,vx,vy,vz,r_AU\n";
//    }
//
//    std::vector<Position> prev(N);
//
//    // ---------- Simulation ----------
//    for (float t = 0; t <= 365.0f; t += 5.0f) {
//
//        glUniform1f(loc_t, t);
//        glDispatchCompute(groups, 1, 1);
//        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT);
//
//        Position* p = (Position*)glMapBufferRange(
//            GL_SHADER_STORAGE_BUFFER, 0,
//            sizeof(Position) * N, GL_MAP_READ_BIT);
//
//        if (!p) continue;
//
//        std::string date = makeDateString((int)t);
//
//        for (size_t i = 0; i < N; ++i) {
//            if (t == 0) { prev[i] = p[i]; continue; }
//
//            float vx = (p[i].x - prev[i].x) / 5.0f;
//            float vy = (p[i].y - prev[i].y) / 5.0f;
//            float vz = (p[i].z - prev[i].z) / 5.0f;
//            float r = magnitude(p[i].x, p[i].y, p[i].z);
//
//            csv[i] << date << ","
//                << p[i].x << "," << p[i].y << "," << p[i].z << ","
//                << vx << "," << vy << "," << vz << "," << r << "\n";
//
//            prev[i] = p[i];
//        }
//
//        glUnmapBuffer(GL_SHADER_STORAGE_BUFFER);
//    }
//
//    for (auto& f : csv) f.close();
//
//    std::cout << "[DONE] Manual results generated for ALL asteroids\n";
//
//    glfwTerminate();
//    return 0;
//}
