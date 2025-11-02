#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cmath>
#include <filesystem>
#include <map>
#include <GL/glew.h>
#include <GLFW/glfw3.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;
namespace fs = std::filesystem;
#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

const unsigned int LOCAL_SIZE_X = 256;
const float RENDER_POINT_SIZE = 3.0f;
const float VISUAL_SCALE = 1.0f;
const std::string DATA_DIR = "data";

struct OrbitalElements { float a, e, i, Omega, omega, M0; };
struct Position { float x, y, z, w; };

const char* computeShaderSrc = R"(
#version 430 core
layout(local_size_x = 256) in;
struct OrbitalElements { float a; float e; float i; float Omega; float omega; float M0; };
layout(std430, binding = 0) readonly buffer OrbElements { OrbitalElements elements[]; };
layout(std430, binding = 1) writeonly buffer Positions { vec4 pos[]; };
uniform float t_days;
const float TWO_PI = 6.28318530717958647692;
float solveE(float M, float e) {
    float E = M; if (E > 3.14159265) E -= TWO_PI;
    for (int k = 0; k < 20; ++k) {
        float f = E - e * sin(E) - M;
        float df = 1.0 - e * cos(E);
        float dE = -f / df;
        E += dE;
        if (abs(dE) < 1e-7) break;
    }
    return E;
}
void main() {
    uint gid = gl_GlobalInvocationID.x;
    OrbitalElements oe = elements[gid];
    const float k = 0.01720209895;
    float n = k / pow(oe.a, 1.5);
    float M = mod(oe.M0 + n * t_days, TWO_PI);
    float E = solveE(M, oe.e);
    float cosE = cos(E), sinE = sin(E);
    float x_orb = oe.a * (cosE - oe.e);
    float y_orb = oe.a * sqrt(max(0.0, 1.0 - oe.e * oe.e)) * sinE;
    float cosO = cos(oe.Omega), sinO = sin(oe.Omega);
    float cosw = cos(oe.omega), sinw = sin(oe.omega);
    float cosi = cos(oe.i), sini = sin(oe.i);
    float m00 = cosO * cosw - sinO * sinw * cosi;
    float m01 = -cosO * sinw - sinO * cosw * cosi;
    float m10 = sinO * cosw + cosO * sinw * cosi;
    float m11 = -sinO * sinw + cosO * cosw * cosi;
    float m20 = sinw * sini;
    float m21 = cosw * sini;
    float x = m00 * x_orb + m01 * y_orb;
    float y = m10 * x_orb + m11 * y_orb;
    float z = m20 * x_orb + m21 * y_orb;
    pos[gid] = vec4(x, y, z, 1.0);
}
)";

const char* vertexShaderSrc = R"(
#version 430 core
layout(location = 0) in vec4 in_pos;
uniform float scale;
uniform mat4 MVP;
void main() {
    vec4 p = in_pos * scale;
    gl_Position = MVP * vec4(p.xyz, 1.0);
    gl_PointSize = 3.0;
}
)";

const char* fragmentShaderSrc = R"(
#version 430 core
out vec4 out_color;
void main() { out_color = vec4(1.0, 0.85, 0.2, 1.0); }
)";

GLuint compileShader(GLenum stage, const char* src) {
    GLuint s = glCreateShader(stage);
    glShaderSource(s, 1, &src, nullptr);
    glCompileShader(s);
    GLint ok; glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        GLint len; glGetShaderiv(s, GL_INFO_LOG_LENGTH, &len);
        std::string log(len, ' ');
        glGetShaderInfoLog(s, len, nullptr, &log[0]);
        std::cerr << log << "\n";
        glDeleteShader(s);
        return 0;
    }
    return s;
}
GLuint linkProgram(GLuint vs, GLuint fs) {
    GLuint p = glCreateProgram();
    glAttachShader(p, vs);
    glAttachShader(p, fs);
    glLinkProgram(p);
    GLint ok; glGetProgramiv(p, GL_LINK_STATUS, &ok);
    if (!ok) {
        GLint len; glGetProgramiv(p, GL_INFO_LOG_LENGTH, &len);
        std::string log(len, ' ');
        glGetProgramInfoLog(p, len, nullptr, &log[0]);
        std::cerr << log << "\n";
        glDeleteProgram(p);
        return 0;
    }
    return p;
}

bool readOrbitalElementsFromJSON(const fs::path& path, OrbitalElements& oe) {
    std::ifstream ifs(path);
    if (!ifs.is_open()) return false;
    json j; ifs >> j;
    std::map<std::string, float> mapv;
    if (j.contains("orbit") && j["orbit"].contains("elements")) {
        for (auto& el : j["orbit"]["elements"]) {
            if (!el.contains("name") || !el.contains("value")) continue;
            std::string name = el["name"];
            float v = el["value"].is_string()
                ? std::stof(el["value"].get<std::string>())
                : static_cast<float>(el["value"].get<double>());
            mapv[name] = v;
        }
    }
    oe.a = mapv["a"];
    oe.e = mapv["e"];
    oe.i = mapv["i"] * (float)(M_PI / 180.0f);
    oe.Omega = mapv["om"] * (float)(M_PI / 180.0f);
    oe.omega = mapv["w"] * (float)(M_PI / 180.0f);
    oe.M0 = mapv["ma"] * (float)(M_PI / 180.0f);
    return true;
}

void ortho(float l, float r, float b, float t, float n, float f, float m[16]) {
    for (int i = 0; i < 16; ++i) m[i] = 0.0f;
    m[0] = 2.0f / (r - l);
    m[5] = 2.0f / (t - b);
    m[10] = -2.0f / (f - n);
    m[12] = -(r + l) / (r - l);
    m[13] = -(t + b) / (t - b);
    m[14] = -(f + n) / (f - n);
    m[15] = 1.0f;
}
std::string makeDateString(int days) {
    int year = 2025;
    int month = 1;
    int day = 1 + days;

    while (day > 30) {
        day -= 30;
        month++;
        if (month > 12) {
            month = 1;
            year++;
        }
    }

    char buf[32];
    snprintf(buf, sizeof(buf), "%04d-%02d-%02d", year, month, day);
    return std::string(buf);
}

float magnitude(float x, float y, float z) {
    return std::sqrt(x * x + y * y + z * z);
}
int main() {
    if (!glfwInit()) return -1;
    glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
    glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 3);
    glfwWindowHint(GLFW_OPENGL_PROFILE, GLFW_OPENGL_CORE_PROFILE);
    GLFWwindow* window = glfwCreateWindow(800, 600, "Asteroid GPU Simulation", nullptr, nullptr);
    if (!window) return -1;
    glfwMakeContextCurrent(window);
    glewExperimental = GL_TRUE;
    if (glewInit() != GLEW_OK) return -1;

    // Read asteroid names from targets.txt
    std::vector<std::string> targetAsteroids;
    std::ifstream targetFile("C:/Users/JASMINE/Desktop/RnD_asteroid/targets.txt");
    if (!targetFile.is_open()) {
        std::cerr << "Error: Could not open targets.txt\n";
        return -1;
    }
    std::string asteroidName;
    while (std::getline(targetFile, asteroidName)) {
        if (!asteroidName.empty()) {
            // Convert spaces to underscores, match JSON filenames
            for (auto& c : asteroidName)
                if (c == ' ') c = '_';
            targetAsteroids.push_back(asteroidName + ".json");
        }
    }
    targetFile.close();


    // Load orbital elements
    std::vector<OrbitalElements> elements;
    for (auto& name : targetAsteroids) {
        fs::path path = fs::path(DATA_DIR) / name;
        OrbitalElements oe{};
        if (readOrbitalElementsFromJSON(path, oe)) elements.push_back(oe);
    }
    size_t N = elements.size();
    if (N == 0) {
        std::cerr << "No orbital data loaded.\n";
        return -1;
    }

    // GPU buffers
    GLuint ssboElems, ssboPos;
    glGenBuffers(1, &ssboElems);
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssboElems);
    glBufferData(GL_SHADER_STORAGE_BUFFER, sizeof(OrbitalElements) * N, elements.data(), GL_STATIC_DRAW);
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 0, ssboElems);

    std::vector<Position> pos(N, { 0,0,0,1 });
    glGenBuffers(1, &ssboPos);
    glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssboPos);
    glBufferData(GL_SHADER_STORAGE_BUFFER, sizeof(Position) * N, pos.data(), GL_DYNAMIC_COPY);
    glBindBufferBase(GL_SHADER_STORAGE_BUFFER, 1, ssboPos);

    // Compute shader setup
    GLuint cs = compileShader(GL_COMPUTE_SHADER, computeShaderSrc);
    GLuint prog = glCreateProgram();
    glAttachShader(prog, cs);
    glLinkProgram(prog);
    glUseProgram(prog);
    GLint loc_t = glGetUniformLocation(prog, "t_days");

    // Create output directory
    std::string saveDir = "C:\\Users\\JASMINE\\Desktop\\RnD_asteroid\\results\\manual";
    fs::create_directories(saveDir);

    GLuint groups = (GLuint)((N + LOCAL_SIZE_X - 1) / LOCAL_SIZE_X);

    // Prepare CSV files
    std::vector<std::ofstream> csvFiles(N);
    for (size_t i = 0; i < N; ++i) {
        std::string name = targetAsteroids[i].substr(0, targetAsteroids[i].find('.')) + ".csv";
        csvFiles[i].open(fs::path(saveDir) / name);
        csvFiles[i] << "datetime_str,x,y,z,vx,vy,vz,r_AU\n";
    }

    // Simulation parameters
    float t_days = 0.0f;
    const float step_days = 5.0f;
    const float total_days = 365.0f;
    std::vector<Position> prevPos(N, { 0,0,0,1 });

    // Simulation loop
    while (t_days <= total_days) {
        glUseProgram(prog);
        glUniform1f(loc_t, t_days);
        glDispatchCompute(groups, 1, 1);
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT | GL_VERTEX_ATTRIB_ARRAY_BARRIER_BIT);

        // Map positions
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssboPos);
        Position* p = (Position*)glMapBufferRange(GL_SHADER_STORAGE_BUFFER, 0, sizeof(Position) * N, GL_MAP_READ_BIT);
        if (p) {
            std::string dateStr = makeDateString((int)t_days);
            for (size_t i = 0; i < N; ++i) {
                float vx = (p[i].x - prevPos[i].x) / step_days;
                float vy = (p[i].y - prevPos[i].y) / step_days;
                float vz = (p[i].z - prevPos[i].z) / step_days;
                float r = magnitude(p[i].x, p[i].y, p[i].z);
                csvFiles[i] << dateStr << "," << p[i].x << "," << p[i].y << "," << p[i].z << ","
                    << vx << "," << vy << "," << vz << "," << r << "\n";
                prevPos[i] = p[i];
            }
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER);
        }

        t_days += step_days;
        glfwPollEvents();
    }

    // Cleanup
    for (auto& f : csvFiles) f.close();
    glDeleteProgram(prog);
    glDeleteShader(cs);
    glDeleteBuffers(1, &ssboElems);
    glDeleteBuffers(1, &ssboPos);
    glfwDestroyWindow(window);
    glfwTerminate();

    std::cout << "Simulation complete. Results saved to: " << saveDir << "\n";
    return 0;
}
