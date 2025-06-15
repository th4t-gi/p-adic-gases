#include "api.h"

#include <sqlpp11/functions.h>
#include <sqlpp11/insert.h>
#include <sqlpp11/parameter.h>
#include <sqlpp11/remove.h>
#include <sqlpp11/select.h>

std::string vectorToJsonString(const auto& vec) {
  std::string result;
  result.reserve(vec.size() * 8);
  result += "[";
  for (size_t i = 0; i < vec.size(); ++i) {
    if (i > 0) result += ",";
    result += std::to_string(vec[i]);
  }
  result += "]";
  return result;
}

TreesApi::TreesApi(std::string filename, bool verbose, std::string outDir)
    : db([&] {
        sqlpp::sqlite3::connection_config config;
        config.path_to_database = filename;
        config.flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE;
        return connection{config};
      }()),
      filename{filename},
      verbose{verbose},
      outDir{outDir} {
  init();
}

void TreesApi::init() {
  // create db if not created fron ddl.txt;
  std::ifstream file("ddl.txt");

  if (file.is_open()) {
    std::string sql = "";
    std::string line;

    while (std::getline(file, line)) {
      sql += line + "\n";
      // if we've reached the end of a statement
      if (line.back() == ';') {
        db.execute(sql);
        sql = "";
      }
    }
    file.close();
  }
}

void TreesApi::import_csv(const std::string& file, const std::string& dbname, char seperator) {
  std::string cmd = std::format(
    "sqlite3 {} '.mode csv' '.separator {}' '.import --skip 1 {}/{} {}' 2>/dev/null",
    this->filename,
    std::string{seperator},
    outDir,
    file,
    dbname
  );
  if (verbose) std::cout << "[import] " << cmd << std::endl;
  system(cmd.c_str());

  int count = db(select(sqlpp::count(1)).from(trees).unconditionally()).front().count;

  if (verbose) std::cout << "[import] Imported " << count << " rows" << std::endl;
}

void TreesApi::export_csv(const std::string& file, const std::string& dbname, char seperator) {
  std::string cmd = std::format(
    "sqlite3 -header -csv -separator {} {} 'select * from {};' > {}/{}",
    std::string{seperator},
    this->filename,
    dbname,
    outDir,
    file
  );
  if (verbose) std::cout << "[export] " << cmd << std::endl;
  system(cmd.c_str());
  if (verbose) std::cout << "[export] exported to " << file << std::endl;
}

void TreesApi::reset_trees(label_size_t labelSize) {
  std::string name = trees::Trees::_alias_t::_literal;

  if (verbose) std::cout << "[reset] resetting trees to N = " << std::to_string(labelSize) << std::endl;
  db(remove_from(trees).where(trees.labelSize > labelSize));

  int count = db(select(sqlpp::count(1)).from(trees).unconditionally()).front().count;

  auto query =
    sqlpp::verbatim("UPDATE SQLITE_SEQUENCE SET SEQ=" + std::to_string(count) + " WHERE NAME='" + name + "'");
  db.execute(query);
}

label_size_t TreesApi::get_max_label_size() {
  auto result = db(select(max(trees.labelSize)).from(trees).unconditionally());

  if (!result.empty()) {
    return result.front().max;
  }
  return 0;
}

std::vector<Tree> TreesApi::get_trees(label_size_t labelSize) {
  auto start = std::chrono::steady_clock::now();
  auto select_stmt = db.prepare(select(all_of(trees)).from(trees).where(trees.labelSize == labelSize));

  std::vector<Tree> out;
  for (auto& row : db(select_stmt)) {
    std::vector<code_t> branches = json::parse(row.branches.text).get<std::vector<code_t>>();
    std::vector<degree_t> degrees = json::parse(row.degrees.text).get<std::vector<degree_t>>();
    Tree new_tree(branches, row.labelSize.value(), degrees);

    out.push_back(new_tree);
  }

  auto end = std::chrono::steady_clock::now();
  auto diff = end - start;

  double duration = std::chrono::duration<double, std::milli>(diff).count();
  if (verbose)
  std::cout << "[get_trees] setSize=" << std::to_string(labelSize) << " " << duration << " ms" << std::endl;

  return out;
}

int TreesApi::insert_tree(const Tree& t) {
  auto start = std::chrono::steady_clock::now();
  trees::Trees trees;
  json branchesArr = t.branches;
  json degreesArr = t.degrees;

  try {
    db(insert_into(trees).set(
      trees.labelSize = static_cast<int64_t>(t.setSize),
      trees.branches = branchesArr.dump(),
      trees.degrees = degreesArr.dump()
    ));
  } catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }

  auto end = std::chrono::steady_clock::now();
  auto diff = end - start;

  double duration = std::chrono::duration<double, std::milli>(diff).count();

  if (verbose) std::cout << "[insert_tree] b=" + t.to_string() << " " << duration << " ms" << std::endl;

  return 0;
}

int TreesApi::insert_trees(const std::vector<Tree>& tr) {
  auto start = std::chrono::steady_clock::now();
  trees::Trees trees;

  static constexpr size_t CHUNK_SIZE = 100000;

  for (int i = 0; i < tr.size(); i += CHUNK_SIZE) {
    auto multi_insert = insert_into(trees).columns(trees.labelSize, trees.branches, trees.degrees);
    multi_insert.values._data._insert_values.reserve(tr.size());

    for (int j = i; j < i + CHUNK_SIZE && j < tr.size(); ++j) {
      const Tree& t = tr[j];

      multi_insert.values.add(
        trees.labelSize = static_cast<int64_t>(t.setSize),
        trees.branches = vectorToJsonString(t.branches),
        trees.degrees = vectorToJsonString(t.degrees)
      );
    }

    try {
      db.execute("BEGIN TRANSACTION");
      db(multi_insert);
      db.execute("COMMIT");
      if (verbose) std::cout << "\r    [insert] batch " << i / CHUNK_SIZE + 1 << " saved" << std::flush;
    } catch (const std::exception& e) {
      std::cerr << e.what() << std::endl;
      return 1;
    }
  }

  auto end = std::chrono::steady_clock::now();
  auto diff = end - start;

  double duration = std::chrono::duration<double, std::milli>(diff).count();

  if (verbose) std::cout << "\n[insert_trees] " << duration << " ms" << std::endl;

  return 0;
}

namespace trees {

auto get_block(connection& db, int id = 0) {
  trees::Blocks blocks;
  auto select_stmt = db.prepare(select(all_of(blocks)).from(blocks).where(blocks.blockId == parameter(blocks.blockId)));

  select_stmt.params.blockId = id;
  return db(select_stmt);
}

int insert_block(connection& db, int id, std::string setStr, int size) {
  trees::Blocks blocks;

  try {
    auto insert_stmt = db.prepare(insert_into(blocks).set(
      blocks.blockId = parameter(blocks.blockId),
      blocks.setStr = parameter(blocks.setStr),
      blocks.labelSize = parameter(blocks.labelSize)
    ));

    insert_stmt.params.blockId = id;
    insert_stmt.params.setStr = setStr;
    insert_stmt.params.labelSize = size;

    db(insert_stmt);
  } catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }

  return 0;
}
}  // namespace trees