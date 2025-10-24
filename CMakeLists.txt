cmake_minimum_required(VERSION 3.22)
project(AsteroidSim VERSION 1.0 LANGUAGES CXX)

# Set C++ standard
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Force 64-bit build
if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(FATAL_ERROR "This project requires a 64-bit build")
endif()

# Use vcpkg toolchain automatically if not set
if(NOT DEFINED CMAKE_TOOLCHAIN_FILE)
    if(DEFINED ENV{VCPKG_ROOT})
        set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")
    else()
        message(FATAL_ERROR "Please set VCPKG_ROOT environment variable or define CMAKE_TOOLCHAIN_FILE")
    endif()
endif()

# Find packages installed via vcpkg
find_package(glfw3 CONFIG REQUIRED)
find_package(glad CONFIG REQUIRED)

# Add executable
add_executable(AsteroidSim
    src/main.cpp
    src/glad.c           # glad.c is in src
 "src/shader.h")

# Include directories
target_include_directories(AsteroidSim PRIVATE
    external/glad        # glad.h is here
)

# Link libraries
target_link_libraries(AsteroidSim PRIVATE
    glfw
    glad::glad
    opengl32
)

# Enable multi-configuration support
set_property(TARGET AsteroidSim PROPERTY VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")

# Specify output directories per configuration
set_target_properties(AsteroidSim PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_BINARY_DIR}/Debug"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/Release"
)
