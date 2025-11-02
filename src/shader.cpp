#include "shader.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <GL/glew.h>

static void printGLError(const char* where) {
    GLenum e = glGetError();
    if (e != GL_NO_ERROR) {
        std::cerr << "GL error at " << where << ": 0x" << std::hex << e << std::dec << "\n";
    }
}

GLuint loadComputeShader(const std::string& path) {
    std::cout << "Attempting to load compute shader from: " << path << "\n";

    std::ifstream file(path);
    if (!file.is_open()) {
        std::cerr << "❌ Failed to open compute shader file: " << path << "\n";
        return 0;
    }

    std::stringstream buffer;
    buffer << file.rdbuf();
    std::string source = buffer.str();
    file.close();
    std::cout << "✅ Shader source loaded (" << source.size() << " bytes)\n";

    // Create and compile
    GLuint shader = glCreateShader(GL_COMPUTE_SHADER);
    const char* src = source.c_str();
    glShaderSource(shader, 1, &src, nullptr);
    glCompileShader(shader);

    // Get compile log length and contents
    GLint compileStatus = GL_FALSE;
    glGetShaderiv(shader, GL_COMPILE_STATUS, &compileStatus);
    GLint compileLogLen = 0;
    glGetShaderiv(shader, GL_INFO_LOG_LENGTH, &compileLogLen);
    if (compileLogLen > 1) {
        std::vector<char> clog(compileLogLen);
        glGetShaderInfoLog(shader, compileLogLen, nullptr, clog.data());
        std::cerr << "🟡 Compute shader compile log:\n" << clog.data() << "\n";
    }
    if (compileStatus != GL_TRUE) {
        std::cerr << "❌ Compute shader compilation FAILED.\n";
        glDeleteShader(shader);
        printGLError("after compile failure");
        return 0;
    }

    // Create program and link
    GLuint program = glCreateProgram();
    glAttachShader(program, shader);
    glLinkProgram(program);

    // Link log
    GLint linkStatus = GL_FALSE;
    glGetProgramiv(program, GL_LINK_STATUS, &linkStatus);
    GLint linkLogLen = 0;
    glGetProgramiv(program, GL_INFO_LOG_LENGTH, &linkLogLen);
    if (linkLogLen > 1) {
        std::vector<char> llog(linkLogLen);
        glGetProgramInfoLog(program, linkLogLen, nullptr, llog.data());
        std::cerr << "🟡 Program link log:\n" << llog.data() << "\n";
    }
    if (linkStatus != GL_TRUE) {
        std::cerr << "❌ Program linking FAILED.\n";
        glDeleteShader(shader);
        glDeleteProgram(program);
        printGLError("after link failure");
        return 0;
    }

    // Validate program (helpful — prints issues that link may not)
    glValidateProgram(program);
    GLint validateStatus = GL_FALSE;
    glGetProgramiv(program, GL_VALIDATE_STATUS, &validateStatus);
    GLint validateLogLen = 0;
    glGetProgramiv(program, GL_INFO_LOG_LENGTH, &validateLogLen);
    if (validateLogLen > 1) {
        std::vector<char> vlog(validateLogLen);
        glGetProgramInfoLog(program, validateLogLen, nullptr, vlog.data());
        std::cerr << "🟡 Program validate log:\n" << vlog.data() << "\n";
    }
    if (validateStatus != GL_TRUE) {
        std::cerr << "❌ Program validation FAILED.\n";
        glDeleteShader(shader);
        glDeleteProgram(program);
        printGLError("after validate failure");
        return 0;
    }

    // Final check
    printGLError("after successful link/validate");

    // Cleanup shader object (kept program)
    glDetachShader(program, shader);
    glDeleteShader(shader);

    std::cout << "✅ Compute shader linked & validated successfully.\n";
    return program;
}
