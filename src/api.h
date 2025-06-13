#pragma once

#include <sqlpp11/functions.h>
#include <sqlpp11/insert.h>
#include <sqlpp11/parameter.h>
#include <sqlpp11/select.h>
#include <sqlpp11/sqlite3/connection.h>

#include <json.hpp>
#include <string>

#include "db.h"
#include "tree.h"
#include "utils.h"

using json = nlohmann::json;
using connection = sqlpp::sqlite3::connection;

namespace trees {

auto get_block(connection& db, int id);
int insert_block(connection& db, int id, std::string setStr, int size);

void reset_trees(connection& db, label_size_t size = 0);
std::vector<Tree> get_trees(connection& db, label_size_t setSize);
label_size_t get_max_label_size(connection& db);

int insert_tree(connection& db, const Tree& t);
int insert_trees(connection& db, const std::vector<Tree>& tr);

}  // namespace trees