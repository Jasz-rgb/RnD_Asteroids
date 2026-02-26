#define _SILENCE_CXX17_CODECVT_HEADER_DEPRECATION_WARNING

#include "main_functions.h"

#include <fstream>
#include <iostream>
#include <map>
#include <cmath>
#include <filesystem>
#include <chrono>
#include <iomanip>
#include <sstream>

#include <nlohmann/json.hpp>

// OpenGL loader (use glad if that’s what your project uses)
#include <GL/glew.h>

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

namespace fs = std::filesystem;
using json = nlohmann::json;

/* ================= SHADER ================= */

GLuint compileShader(GLenum stage, const char* src) {
    GLuint s = glCreateShader(stage);
    glShaderSource(s, 1, &src, nullptr);
    glCompileShader(s);

    GLint ok;
    glGetShaderiv(s, GL_COMPILE_STATUS, &ok);
    if (!ok) {
        GLint len;
        glGetShaderiv(s, GL_INFO_LOG_LENGTH, &len);
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

    GLint ok;
    glGetProgramiv(p, GL_LINK_STATUS, &ok);
    if (!ok) {
        GLint len;
        glGetProgramiv(p, GL_INFO_LOG_LENGTH, &len);
        std::string log(len, ' ');
        glGetProgramInfoLog(p, len, nullptr, &log[0]);
        std::cerr << log << "\n";
        glDeleteProgram(p);
        return 0;
    }
    return p;
}

/* ================= ORBIT ================= */

bool readOrbitalElementsFromJSON(const fs::path& path, OrbitalElements& oe) {
    std::ifstream ifs(path);
    if (!ifs.is_open()) return false;

    json j;
    ifs >> j;

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
    oe.i = mapv["i"] * float(M_PI / 180.0);
    oe.Omega = mapv["om"] * float(M_PI / 180.0);
    oe.omega = mapv["w"] * float(M_PI / 180.0);
    oe.M0 = mapv["ma"] * float(M_PI / 180.0);

    return true;
}

/* ================= MATRIX ================= */

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

/* ================= DATE (FIXED) ================= */

#include <ctime>
#include <sstream>
#include <iomanip>

std::string makeDateString(int days_from_start) {
    std::tm t = {};
    t.tm_year = 2025 - 1900;  // years since 1900
    t.tm_mon = 0;            // January
    t.tm_mday = 1 + days_from_start;

    std::mktime(&t); // normalizes date (handles month/year overflow)

    std::ostringstream oss;
    oss << std::setw(4) << (t.tm_year + 1900) << "-"
        << std::setw(2) << std::setfill('0') << (t.tm_mon + 1) << "-"
        << std::setw(2) << std::setfill('0') << t.tm_mday;

    return oss.str();
}

/* ================= MATH ================= */

float magnitude(float x, float y, float z) {
    return std::sqrt(x * x + y * y + z * z);
}
