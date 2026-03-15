#pragma once

#include <SQLiteCpp/SQLiteCpp.h>
#include <spdlog/fmt/chrono.h>
#include <spdlog/spdlog.h>
#include <spdlog/stopwatch.h>

#include <format>
#include <iostream>
#include <json.hpp>
#include <string>
#include <vector>

#include "tree.h"
#include "utils.h"

using json = nlohmann::json;

class APIWrapper {
 public:
  static const size_t BATCH_READ_SIZE = 10000;
  static const size_t BATCH_COMPUTE_SIZE = 500000;
  static const size_t BATCH_WRITE_SIZE = 100000;

  bool verbose;
  SQLite::Database db;

  APIWrapper(std::string dbpath, bool verbose = false);
  std::string getDBpath();

  int get_max_label_size();
  Tree get_tree(uint64_t treeId, label_size_t labelSize, bool is_filtered = false);
  std::vector<Tree> get_trees(label_size_t labelSize, bool is_filtered = false);
  std::string get_tree_table(label_size_t labelSize, bool is_filtered = false);

  int insert_tree(const Tree& t, bool is_filtered = false);
  int insert_trees(
    const std::vector<Tree>& trees, label_size_t labelSize, bool is_filtered = false
  );
  void reset_trees(label_size_t labelSize = 0);
  void create_tree_table(label_size_t labelSize, bool is_filtered = false);

  void import_csv(const std::string& file, const std::string& tablename, char seperator);
  void export_csv(const std::string& file, const std::string& tablename, char seperator);

 private:
  inline static constexpr const char* treesSchema =
    "CREATE TABLE IF NOT EXISTS {} ("
    "branches JSON NOT NULL,"
    "degrees JSON NOT NULL"
    ");";
  // "id INTEGER PRIMARY KEY AUTOINCREMENT,"
  inline static constexpr const char* metaSchema =
    "CREATE TABLE IF NOT EXISTS trees_sequence ("
    "name TEXT PRIMARY KEY,"
    "label_size INTEGER NOT NULL,"
    "is_filtered BOOLEAN DEFAULT 0"
    ");";

  std::string outDir = "./out/";
  std::string dbpath;
};
