cmake_minimum_required(VERSION 3.12)

set(CMAKE_BUILD_TYPE "RelWithDebInfo" CACHE STRING
  "One of Debug, Release, [RelWithDebInfo], and MinSizeRel")
set(CMAKE_C_FLAGS "-Wall -Wextra" CACHE STRING "C compiler flags")

project(JBCS C)

find_package(OpenMP REQUIRED)

foreach(app IN ITEMS pi mandel)
  add_executable(${app} ${app}.c)
  target_compile_options(${app} PRIVATE -fdiagnostics-color=always)
  target_link_libraries(${app} OpenMP::OpenMP_C m)
endforeach()
