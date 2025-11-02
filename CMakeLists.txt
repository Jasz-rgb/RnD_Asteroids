cmake_minimum_required(VERSION 3.22)
project(AsteroidSim VERSION 1.0 LANGUAGES CXX)

# --- Compiler setup ---
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)

# Force MSVC to use /std:c++17 explicitly
if (MSVC)
    add_compile_options(/std:c++17)
endif()

# --- Architecture check ---
if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(FATAL_ERROR "This project requires a 64-bit build")
endif()

# --- Paths to dependencies ---
set(GLEW_INCLUDE_DIR "C:/Users/JASMINE/Desktop/RnD_asteroid/include/glew")
set(GLEW_LIB_DIR     "C:/Users/JASMINE/Desktop/RnD_asteroid/libs")
set(GLFW_INCLUDE_DIR "C:/Users/JASMINE/Desktop/RnD_asteroid/include/glfw")
set(NLOHMANN_INCLUDE_DIR "C:/Users/JASMINE/Desktop/RnD_asteroid/include/nlohmann")

# --- Executable sources ---
add_executable(AsteroidSim
    src/main.cpp
    src/shader.cpp
    src/shader.h
    src/glad.c
)

# --- Include directories ---
target_include_directories(AsteroidSim PRIVATE
    ${GLEW_INCLUDE_DIR}
    ${GLFW_INCLUDE_DIR}
    ${NLOHMANN_INCLUDE_DIR}
    external
    external/glad
)

# --- Link directories and libraries ---
link_directories(${GLEW_LIB_DIR})
target_link_libraries(AsteroidSim PRIVATE
    glew32
    glfw3
    opengl32
)

# --- Set working directory ---
set_property(TARGET AsteroidSim PROPERTY VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")

# --- Set output directories ---
set_target_properties(AsteroidSim PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_BINARY_DIR}/Debug"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/Release"
)
