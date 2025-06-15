#include "logger.h"

namespace logger {

static std::string logDir = "logs";
static std::string console_pattern = "[%T.%e] [%^%l%$] [%!] %v";
static std::string file_pattern = "[%b %d %T.%e] [%l] [%!] %v";

std::shared_ptr<spdlog::logger> file_out;
std::shared_ptr<spdlog::logger> logger;

void init(const std::string& log_file, spdlog::level::level_enum level) {
  //Create console sink (if verbose: debug, else: info)
  auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
  console_sink->set_pattern(console_pattern);
  console_sink->set_level(level);

  // Create file sink (every level)
  auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(unique_log_filename(log_file), true);
  file_sink->set_pattern(file_pattern);
  file_sink->set_level(spdlog::level::trace);

  file_out = std::make_shared<spdlog::logger>("file_only", file_sink);

  // Combine sinks
  std::vector<spdlog::sink_ptr> sinks{console_sink, file_sink};
  logger = std::make_shared<spdlog::logger>("app", sinks.begin(), sinks.end());
  logger->set_level(spdlog::level::trace);
  spdlog::set_default_logger(logger);

  spdlog::flush_on(spdlog::level::warn);
}

std::shared_ptr<spdlog::logger> get() { return logger; }

std::string unique_log_filename(const std::string& filename) {
  auto now = std::chrono::system_clock::now();
  auto t = std::chrono::system_clock::to_time_t(now);

  std::ostringstream oss;
  oss << logDir << "/" << filename << "_" << std::put_time(std::localtime(&t), "%m%d_%H%M%S") << ".log";
  return oss.str();
}

void preamble(std::string cmd, std::string change) {
  file_out->set_pattern("%v");

  file_out->info("BUILD INFO: {} {}", GIT_HASH, GIT_MSG);
  file_out->info("COMMAND: {}", cmd);

  if (!change.empty()) {
    file_out->info("DESCRIPTION: {}", change);
  }

  file_out->info("######################################################################");
  file_out->set_pattern(file_pattern);
}

}  // namespace logger
