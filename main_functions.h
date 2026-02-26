#pragma once
#include <string>
#include <cmath>
#include <filesystem>
#include <GL/glew.h>

struct OrbitalElements { float a, e, i, Omega, omega, M0; };

GLuint compileShader(GLenum stage, const char* src);
GLuint linkProgram(GLuint vs, GLuint fs);
bool readOrbitalElementsFromJSON(const std::filesystem::path& path, OrbitalElements& oe);
void ortho(float l, float r, float b, float t, float n, float f, float m[16]);
std::string makeDateString(int days);
float magnitude(float x, float y, float z);
//std::string normalizeName(const std::string& input);