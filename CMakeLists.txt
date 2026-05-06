cmake_minimum_required(VERSION 3.20)
project(padic_gas CXX)

set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Output all binaries directly into build/ (mirrors old Makefile layout)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR})

if(NOT CMAKE_BUILD_TYPE)
  set(CMAKE_BUILD_TYPE Release)
endif()

# ---------------------------------------------------------------------------
# Platform helpers
# ---------------------------------------------------------------------------

# macOS: auto-detect Homebrew prefix (works on both Intel and Apple Silicon)
if(APPLE)
  execute_process(
    COMMAND brew --prefix
    OUTPUT_VARIABLE HOMEBREW_PREFIX
    OUTPUT_STRIP_TRAILING_WHITESPACE
    ERROR_QUIET
  )
  if(HOMEBREW_PREFIX)
    list(APPEND CMAKE_PREFIX_PATH ${HOMEBREW_PREFIX})
  endif()
endif()

# Windows: vcpkg is the recommended way to install SQLite3, SQLiteCpp, Boost.
# Pass -DCMAKE_TOOLCHAIN_FILE=<vcpkg>/scripts/buildsystems/vcpkg.cmake at
# configure time, or set the VCPKG_ROOT environment variable.
if(WIN32 AND DEFINED ENV{VCPKG_ROOT} AND NOT DEFINED CMAKE_TOOLCHAIN_FILE)
  set(CMAKE_TOOLCHAIN_FILE "$ENV{VCPKG_ROOT}/scripts/buildsystems/vcpkg.cmake" CACHE STRING "")
endif()

# ---------------------------------------------------------------------------
# Git metadata → generated header (avoids compiler-specific quoting issues)
# ---------------------------------------------------------------------------
find_package(Git QUIET)
set(GIT_HASH "unknown")
set(GIT_MSG  "unknown")
if(Git_FOUND)
  execute_process(
    COMMAND ${GIT_EXECUTABLE} rev-parse --short HEAD
    OUTPUT_VARIABLE GIT_HASH OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET
  )
  execute_process(
    COMMAND ${GIT_EXECUTABLE} log -1 --pretty=%s
    OUTPUT_VARIABLE GIT_MSG OUTPUT_STRIP_TRAILING_WHITESPACE ERROR_QUIET
  )
endif()
configure_file(cmake/git_info.h.in ${CMAKE_BINARY_DIR}/git_info.h @ONLY)

# ---------------------------------------------------------------------------
# System-level dependencies (SQLite3, SQLiteCpp, Boost)
# These are best installed via the system package manager or vcpkg on Windows.
# ---------------------------------------------------------------------------
find_package(SQLite3   REQUIRED)
find_package(SQLiteCpp REQUIRED)
find_package(Boost     REQUIRED COMPONENTS program_options)

# ---------------------------------------------------------------------------
# fmt, spdlog, nlohmann_json — try system install, fall back to FetchContent
# ---------------------------------------------------------------------------
include(FetchContent)

find_package(fmt QUIET)
if(NOT fmt_FOUND)
  FetchContent_Declare(fmt
    GIT_REPOSITORY https://github.com/fmtlib/fmt.git
    GIT_TAG        11.0.2
    GIT_SHALLOW    TRUE
  )
  FetchContent_MakeAvailable(fmt)
endif()

find_package(spdlog QUIET)
if(NOT spdlog_FOUND)
  FetchContent_Declare(spdlog
    GIT_REPOSITORY https://github.com/gabime/spdlog.git
    GIT_TAG        v1.15.1
    GIT_SHALLOW    TRUE
  )
  FetchContent_MakeAvailable(spdlog)
endif()

find_package(nlohmann_json QUIET)
if(NOT nlohmann_json_FOUND)
  FetchContent_Declare(nlohmann_json
    GIT_REPOSITORY https://github.com/nlohmann/json.git
    GIT_TAG        v3.11.3
    GIT_SHALLOW    TRUE
  )
  FetchContent_MakeAvailable(nlohmann_json)
endif()

# ---------------------------------------------------------------------------
# Shared core static library
# ---------------------------------------------------------------------------
add_library(core STATIC
  src/utils.cpp
  src/tree.cpp
  src/api.cpp
  src/phylogenees.cpp
  src/logger.cpp
)

target_compile_definitions(core PUBLIC SPDLOG_ACTIVE_LEVEL=SPDLOG_LEVEL_TRACE)

# Generated git_info.h lives in the binary dir
target_include_directories(core PRIVATE ${CMAKE_BINARY_DIR})

target_link_libraries(core PUBLIC
  # SQLite3::SQLite3
  SQLiteCpp
  Boost::program_options
  fmt::fmt
  spdlog::spdlog
  nlohmann_json::nlohmann_json
)

# ---------------------------------------------------------------------------
# Executables
# ---------------------------------------------------------------------------
add_executable(main       src/main.cpp)
add_executable(translate  src/translate.cpp)
add_executable(partitions src/partitions.cpp)

target_link_libraries(main      PRIVATE core)
target_link_libraries(translate PRIVATE core)
# partitions has no external dependencies

# Debug-only test binary (mirrors `make DEBUG=1` behaviour)
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
  add_executable(test src/test.cpp)
  target_link_libraries(test PRIVATE core)
endif()
