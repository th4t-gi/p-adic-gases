#include "trees.h"
#include "utils.h"
#include <sqlpp11/sqlite3/connection.h>
#include <json.hpp>
#include <string>
#include <sqlpp11/select.h>
#include <sqlpp11/insert.h>
#include <sqlpp11/parameter.h>
#include <sqlpp11/functions.h>


using json = nlohmann::json;
using connection = sqlpp::sqlite3::connection;

namespace trees {

  auto get_block(connection& db, int id);
  int insert_block(connection& db, int id, std::string setStr, int size);

  std::vector<Tree> get_trees(connection& db, int setSize);
  int insert_tree(connection& db, Tree& t);

}