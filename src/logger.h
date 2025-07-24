#pragma once

#ifndef GIT_HASH
#define GIT_HASH NULL
#endif  // !GIT_HASH

#ifndef GIT_MSG
#define GIT_MSG NULL
#endif  // !GIT_HASH

#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/spdlog.h>

#include <iomanip>
#include <iostream>
#include <memory>
#include <sstream>
namespace logger {

extern std::shared_ptr<spdlog::logger> logger;
extern std::shared_ptr<spdlog::logger> file_out;

void init(const std::string& log_file = "log.txt", spdlog::level::level_enum level = spdlog::level::info);

std::shared_ptr<spdlog::logger> get();

std::string unique_log_filename(const std::string& filename);

void preamble(std::string cmd, std::string change);

}  // namespace logger