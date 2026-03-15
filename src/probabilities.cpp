#include <sqlpp11/functions.h>
#include <sqlpp11/insert.h>
#include <sqlpp11/parameter.h>
#include <sqlpp11/remove.h>
#include <sqlpp11/select.h>
#include <sqlpp11/sqlite3/connection.h>

#include <iostream>

#include "api.h"

int main(void) {
  int N = 4;

  std::cout << "What do you want N to be? ";
  std::cin >> N;

  std::string dbname_out = "size" + std::to_string(N) + ".db";

  ApiWrapper api{"trees.db"};

  sqlpp::sqlite3::connection_config config;
  config.path_to_database = dbname_out;
  config.flags = SQLITE_OPEN_READWRITE | SQLITE_OPEN_CREATE;

  sqlpp::sqlite3::connection db(config);

  db.execute(R"(
    CREATE TABLE IF NOT EXISTS trees (
      id INTEGER PRIMARY KEY,
      branches JSON NOT NULL,
      degrees JSON NOT NULL
    );
  )");
  db.execute(R"(
    CREATE TABLE IF NOT EXISTS probabilities (
      tree_id INTEGER NOT NULL, 
      prime INTEGER NOT NULL,

      probability REAL DEFAULT 0,

      PRIMARY KEY(tree_id, prime),
      FOREIGN KEY(tree_id) REFERENCES trees(id)
    );
  )");

  trees::Trees treesTable;
  trees::Probabilities probTable;

  // api.db.attach(config, dbname_out);

  for (auto& row : api.db(select(all_of(treesTable)).from(treesTable).where(treesTable.labelSize == N))) {
    // inserts just size N into output database
    db(
      sqlpp::insert_into(treesTable)
        .set(treesTable.branches = row.branches, treesTable.degrees = row.degrees, treesTable.id = row.id)
    );
  }

  std::vector<Tree> tree_arr = api.get_trees(N);

  for (int p : api.primes) {
    for (Tree& t : tree_arr) {
      double probability = t.probability(p);

      db(insert_into(probTable).set(probTable.treeId = t.id, probTable.prime = p, probTable.probability = probability));
    }
  }
}