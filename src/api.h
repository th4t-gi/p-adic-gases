#pragma once

#include <spdlog/spdlog.h>
#include <spdlog/stopwatch.h>
#include <sqlpp11/sqlite3/connection.h>
#include <spdlog/fmt/chrono.h>

#include <format>
#include <fstream>
#include <iostream>
#include <json.hpp>
#include <string>

#include "db.h"
#include "tree.h"
#include "utils.h"

using json = nlohmann::json;
using connection = sqlpp::sqlite3::connection;

class TreesApi {
 public:
  trees::Trees trees;
  std::string filename;
  std::string outDir;
  connection db;
  std::fstream filestream;
  bool verbose;

  TreesApi(std::string filename, bool verbose = false, std::string outDir = "./out");

  void init();
  void import_csv(const std::string& file, const std::string& dbname = "trees", char seperator = ',');
  void export_csv(const std::string& file, const std::string& dbname = "trees", char seperator = ',');
  void reset_trees(label_size_t size = 0);
  std::vector<Tree> get_trees(label_size_t setSize);
  label_size_t get_max_label_size();

  int insert_tree(const Tree& t);
  int insert_trees(const std::vector<Tree>& tr, label_size_t N = 0);
};

namespace trees {
auto get_block(connection& db, int id);
int insert_block(connection& db, int id, std::string setStr, int size);
}  // namespace trees