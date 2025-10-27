cmake_minimum_required(VERSION 3.22)
project(AsteroidSim VERSION 1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

if(NOT CMAKE_SIZEOF_VOID_P EQUAL 8)
    message(FATAL_ERROR "This project requires a 64-bit build")
endif()

set(GLEW_INCLUDE_DIR "C:/Users/JASMINE/Desktop/Project1")
set(GLEW_LIB_DIR     "C:/Users/JASMINE/Desktop/Project1/lib")
set(GLFW_INCLUDE_DIR "C:/Users/JASMINE/Desktop/RnD_asteroid/external/glfw/include")
set(NLOHMANN_INCLUDE_DIR "C:/Users/JASMINE/Desktop/RnD_asteroid/external/nlohmann")

# Add executable
add_executable(AsteroidSim
    src/main.cpp
    src/shader.cpp
    src/shader.h
    src/glad.c       
)

# Include directories
target_include_directories(AsteroidSim PRIVATE
    ${GLEW_INCLUDE_DIR}          # GLEW
    ${GLFW_INCLUDE_DIR}          # GLFW
    ${NLOHMANN_INCLUDE_DIR}      # nlohmann/json
    external                     # other local includes
    external/glad
)

link_directories(${GLEW_LIB_DIR})

target_link_libraries(AsteroidSim PRIVATE
    glew32        # GLEW
    glfw3         # GLFW
    opengl32      # Windows OpenGL
)

set_property(TARGET AsteroidSim PROPERTY VS_DEBUGGER_WORKING_DIRECTORY "${CMAKE_SOURCE_DIR}")

set_target_properties(AsteroidSim PROPERTIES
    RUNTIME_OUTPUT_DIRECTORY_DEBUG "${CMAKE_BINARY_DIR}/Debug"
    RUNTIME_OUTPUT_DIRECTORY_RELEASE "${CMAKE_BINARY_DIR}/Release"
)
