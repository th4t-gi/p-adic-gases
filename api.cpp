#include "api.h"
#include "tree.h"
#include <sqlpp11/custom_query.h>
#include <sqlpp11/select.h>

// int main(void) {
//   sqlpp::sqlite3::connection_config config;
//   config.path_to_database = "trees.db";
//   config.flags = SQLITE_OPEN_READWRITE;


//   trees::Blocks table;
//   connection db(config);

//   // auto query = sqlpp::custom_query("SELECT * FROM trees WHERE id = 1;").with_result_type_of(select(sqlpp::value("").as(table.setStr)));

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

  std::vector<Tree> get_trees(connection& db, int setSize) {
    trees::Trees trees;
    auto select_stmt = db.prepare(select(all_of(trees)).from(trees).where(trees.setSize == parameter(trees.setSize)));

    select_stmt.params.setSize = setSize;

    std::vector<Tree> out;
    json j;
    for (auto& row : db(select_stmt)) {
      std::vector<unsigned int> branches = json::parse(row.branches.text).get<std::vector<unsigned int>>();
      std::vector<int> degrees = json::parse(row.degrees.text).get<std::vector<int>>();
      Tree new_tree(branches, row.setSize.value(), degrees);

      out.push_back(new_tree);
    }
    return out;
  }

  int insert_tree(connection& db, Tree& t) {
    trees::Trees trees;
    json branchesArr = t.branches;
    json degreesArr = t.degrees;
    
    try {
    auto insert_stmt = db.prepare(insert_into(trees).set(
      trees.setSize = parameter(trees.setSize),
      trees.branches = parameter(trees.branches),
      trees.degrees = parameter(trees.degrees)
    ));

    insert_stmt.params.setSize = t.setSize;
    insert_stmt.params.branches = branchesArr.dump();
    insert_stmt.params.degrees = degreesArr.dump(); 

      db(insert_stmt);
    } catch (const std::exception& e) {
      std::cerr << e.what() << std::endl;
      return 1;
    }

    return 0;
  }
}