#include "api.h"

#include <sqlpp11/custom_query.h>
#include <sqlpp11/remove.h>
#include <sqlpp11/select.h>

#include "tree.h"
#include "utils.h"

// int main(void) {
//   sqlpp::sqlite3::connection_config config;
//   config.path_to_database = "trees.db";
//   config.flags = SQLITE_OPEN_READWRITE;

//   trees::Blocks table;
//   connection db(config);

//   // auto query = sqlpp::custom_query("SELECT * FROM trees WHERE id =
//   1;").with_result_type_of(select(sqlpp::value("").as(table.setStr)));

//   // for (const auto& row : db(query)) {
//   //     std::cout << row.setStr << std::endl; // prints: {"a":1,"b":2}
//   // }

// }

// create table
template <std::size_t T>
void create_table(connection& db, std::string name, std::array<std::string, T> cols) {
  std::string sql = "CREATE TABLE " + name + " IF NOT EXISTS (";
  for (std::string s : cols) {
    sql += s + "\n";
  }

  // db.execute()
  // sqlite3_exec(db, sql.c_str(), );
}

namespace trees {

void reset_trees(connection& db, label_size_t size) {
  trees::Trees trees;
  std::string name = trees::Trees::_alias_t::_literal;

  db(sqlpp::remove_from(trees).where(trees.setSize > size));

  int count = db(sqlpp::select(sqlpp::count(1)).from(trees).unconditionally()).front().count;

  auto query =
    sqlpp::verbatim("UPDATE SQLITE_SEQUENCE SET SEQ=" + std::to_string(count) + " WHERE NAME='" + name + "'");
  db.execute(query);
}

label_size_t get_max_label_size(connection& db) {
  trees::Trees trees;
  auto result = db(select(max(trees.setSize)).from(trees).unconditionally());

  if (!result.empty()) {
    return result.front().max;
  }
  return 0;
}

auto get_block(connection& db, int id = 0) {
  trees::Blocks blocks;
  auto select_stmt = db.prepare(select(all_of(blocks)).from(blocks).where(blocks.id == parameter(blocks.id)));

  select_stmt.params.id = id;
  return db(select_stmt);
}

int insert_block(connection& db, int id, std::string setStr, int size) {
  trees::Blocks blocks;

  try {
    auto insert_stmt = db.prepare(insert_into(blocks).set(
      blocks.id = parameter(blocks.id),
      blocks.setStr = parameter(blocks.setStr),
      blocks.setSize = parameter(blocks.setSize)
    ));

    insert_stmt.params.id = id;
    insert_stmt.params.setStr = setStr;
    insert_stmt.params.setSize = size;

    db(insert_stmt);
  } catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }

  return 0;
}

std::vector<Tree> get_trees(connection& db, label_size_t setSize) {
  auto start = std::chrono::steady_clock::now();
  trees::Trees trees;
  auto select_stmt = db.prepare(select(all_of(trees)).from(trees).where(trees.setSize == parameter(trees.setSize)));

  select_stmt.params.setSize = setSize;

  std::vector<Tree> out;
  json j;
  for (auto& row : db(select_stmt)) {
    std::vector<code_t> branches = json::parse(row.branches.text).get<std::vector<code_t>>();
    std::vector<degree_t> degrees = json::parse(row.degrees.text).get<std::vector<degree_t>>();
    Tree new_tree(branches, row.setSize.value(), degrees);

    out.push_back(new_tree);
  }

  auto end = std::chrono::steady_clock::now();
  auto diff = end - start;

  double duration = std::chrono::duration<double, std::milli>(diff).count();

  std::cout << "[get_trees] setSize=" << setSize << " " << duration << " ms" << std::endl;

  return out;
}

int insert_tree(connection& db, const Tree& t) {
  auto start = std::chrono::steady_clock::now();
  trees::Trees trees;
  json branchesArr = t.branches;
  json degreesArr = t.degrees;

  try {
    db(insert_into(trees).set(
      trees.setSize = static_cast<int64_t>(t.setSize),
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

  std::cout << "[insert_tree] b=" + t.to_string() << " " << duration << " ms" << std::endl;

  return 0;
}

int insert_trees(connection& db, const std::vector<Tree>& tr) {
  auto start = std::chrono::steady_clock::now();
  trees::Trees trees;

  static constexpr size_t CHUNK_SIZE = 100000;

  for (int i = 0; i < tr.size(); i += CHUNK_SIZE) {
    auto multi_insert = insert_into(trees).columns(trees.setSize, trees.branches, trees.degrees);
    multi_insert.values._data._insert_values.reserve(tr.size());

    for (int j = i; j < i + CHUNK_SIZE && j < tr.size(); ++j) {
      const Tree& t = tr[j];
      json branchesArr = t.branches;
      json degreesArr = t.degrees;

      multi_insert.values.add(
        trees.setSize = static_cast<int64_t>(t.setSize),
        trees.branches = branchesArr.dump(),
        trees.degrees = degreesArr.dump()
      );
    }

    try {
      db.execute("BEGIN TRANSACTION");
      db(multi_insert);
      db.execute("COMMIT");
      std::cout << "\r    [insert] batch " << i / CHUNK_SIZE + 1 << " saved" << std::flush;
    } catch (const std::exception& e) {
      std::cerr << e.what() << std::endl;
      return 1;
    }
  }

  auto end = std::chrono::steady_clock::now();
  auto diff = end - start;

  double duration = std::chrono::duration<double, std::milli>(diff).count();

  std::cout << "\n[insert_trees] " << duration << " ms" << std::endl;

  return 0;
}
}  // namespace trees