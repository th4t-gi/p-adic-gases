#include "api.h"

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

APIWrapper::APIWrapper(std::string dbpath, bool verbose)
    : dbpath{dbpath}, db{dbpath, SQLite::OPEN_READWRITE | SQLite::OPEN_CREATE} {
  db.exec(metaSchema);
  db.setBusyTimeout(5000);
}

std::string APIWrapper::getDBpath() { return dbpath; }

int APIWrapper::get_max_label_size() { return db.execAndGet("SELECT MAX(label_size) FROM trees_sequence").getInt(); }

Tree APIWrapper::get_tree(uint64_t treeId, label_size_t labelSize, bool is_filtered) {
  spdlog::stopwatch sw;
  std::string tbl_name = get_tree_table(labelSize, is_filtered);
  Tree t;

  if (db.tableExists(tbl_name)) {
    std::string stmt = std::format("SELECT * FROM {} WHERE rowid == {}", tbl_name, treeId);
    SQLite::Statement query(db, stmt);

    query.executeStep();
    t = Tree::fromColumns(query.getColumn(0), query.getColumn(1), query.getColumn(2), query.getColumn(3));
  }

  SPDLOG_DEBUG(
    "loaded tree id {} from label size {} ({}) ({} bytes stack, {} bytes heap)",
    t.id,
    labelSize,
    sw.elapsed_ms(),
    sizeof(t),
    t.branches.capacity() + t.degrees.capacity()
  );

  return t;
}

std::vector<Tree> APIWrapper::get_trees(label_size_t labelSize, bool is_filtered) {
  spdlog::stopwatch sw;
  std::string tbl_name = get_tree_table(labelSize, is_filtered);
  std::vector<Tree> trees;

  if (db.tableExists(tbl_name)) {
    std::string stmt = std::format("SELECT rowid, * FROM {}", tbl_name);
    SQLite::Statement query(db, stmt);

    try {
      while (query.executeStep()) {
        Tree t = Tree::fromColumns(query.getColumn(0), query.getColumn(1), query.getColumn(2), labelSize);
        trees.push_back(t);
      }
    } catch (SQLite::Exception& e) {
      std::cout << e.what() << std::endl;
    }
  }

  // int space = trees.capacity() * sizeof(Tree);
  SPDLOG_DEBUG("loaded {} trees of label size {} ({})", trees.size(), labelSize, sw.elapsed_ms());

  return trees;
}

int APIWrapper::insert_tree(const Tree& t, bool is_filtered) {
  spdlog::stopwatch sw;

  std::string tbl_name = get_tree_table(t.labelSize, is_filtered);
  if (!db.tableExists(tbl_name)) {
    create_tree_table(t.labelSize, is_filtered);
  }

  std::string stmt = std::format("INSERT INTO {} VALUES (?, ?)", tbl_name);
  SQLite::Statement query(db, stmt);

  query.bind(1, vectorToJsonString(t.branches));
  query.bind(2, vectorToJsonString(t.degrees));

  try {
    query.exec();
  } catch (const std::exception& e) {
    std::cerr << e.what() << std::endl;
    return 1;
  }

  SPDLOG_INFO("b={} ({})", t.to_string(), sw);
  return 0;
}

int APIWrapper::insert_trees(const std::vector<Tree>& trees, label_size_t labelSize, bool is_filtered) {
  spdlog::stopwatch sw;
  SPDLOG_DEBUG("saving {} trees", trees.size());

  std::string tbl_name = get_tree_table(labelSize, is_filtered);
  if (!db.tableExists(tbl_name)) {
    create_tree_table(labelSize, is_filtered);
  }

  db.exec("PRAGMA synchronous = OFF");
  db.exec("PRAGMA journal_mode = MEMORY");

  for (int i = 0; i < trees.size(); i += BATCH_WRITE_SIZE) {
    // START BATCH TRANSACTION
    SQLite::Transaction transaction(db);

    std::string stmt = std::format("INSERT INTO {} VALUES (?, ?)", tbl_name);
    SQLite::Statement query(db, stmt);

    for (int j = i; j < i + BATCH_WRITE_SIZE && j < trees.size(); ++j) {
      // insert individual tree
      const Tree& t = trees[j];

      // query.bind(1, (int64_t)t.id);
      query.bind(1, vectorToJsonString(t.branches));
      query.bind(2, vectorToJsonString(t.degrees));

      try {
        query.exec();
        query.reset();
        // std::cout << "\r[insert_trees]" << (labelSize ? " N = " + std::to_string(labelSize) : " ") << " batch "
        //           << i / BATCH_SIZE + 1 << " saved" << std::flush;
      } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;
        return 1;
      }
    }
    transaction.commit();
    // FINISH BATCH TRANSACTION
  }
  // std::cout << std::endl;
  db.exec("PRAGMA synchronous = FULL");

  SPDLOG_INFO("{} batches saved", trees.size() / BATCH_WRITE_SIZE + 1);
  return trees.size();
}

void APIWrapper::reset_trees(label_size_t labelSize) {
  try {
    std::vector<std::string> tables_to_drop;
    {
      // gets all tables with label_size > labelSize
      std::string selectStmt = "SELECT name FROM trees_sequence WHERE label_size > ?";
      SQLite::Statement selectQuery(db, selectStmt);
      selectQuery.bind(1, labelSize);
      while (selectQuery.executeStep()) {
        tables_to_drop.push_back(selectQuery.getColumn(0).getText());
      }
    }

    {  // delete tables while they exist in query
      for (const auto& table : tables_to_drop) {
        std::string dropStmt = std::format("DROP TABLE IF EXISTS {}", table);
        db.exec(dropStmt);
        SPDLOG_DEBUG("dropped table {}", table);
      }
    }

    // delete metadata from trees_sequence
    SQLite::Transaction transaction(db);
    std::string deleteStmt = "DELETE FROM trees_sequence WHERE label_size > ?";
    SQLite::Statement deleteQuery(db, deleteStmt);
    deleteQuery.bind(1, labelSize);
    deleteQuery.exec();
    transaction.commit();

  } catch (const SQLite::Exception& e) {
    std::cout << "o no! an error!";
    std::cerr << e.what() << e.getErrorStr() << '\n';
  }
}

std::string APIWrapper::get_tree_table(label_size_t labelSize, bool is_filtered) {
  return "trees" + std::to_string(labelSize) + (is_filtered ? "_r" : "");
}

void APIWrapper::create_tree_table(label_size_t labelSize, bool is_filtered) {
  std::string tbl_name = get_tree_table(labelSize, is_filtered);

  // Add metadata for table
  SQLite::Statement query(db, "INSERT INTO trees_sequence VALUES (?, ?, ?)");
  query.bind(1, tbl_name);
  query.bind(2, labelSize);
  query.bind(3, is_filtered);
  query.exec();

  // Create table
  std::string stmt = std::format(APIWrapper::treesSchema, tbl_name);
  db.exec(stmt);
}

void TreesApi::import_csv(const std::string& file, const std::string& dbname, char seperator) {
  std::string cmd = "sqlite3 " + this->filename + " '.mode csv' '.separator " + std::string{seperator} +
                    "' '.import --skip 1 " + outDir + "/" + file + " " + dbname + "'";

  // std::string cmd = fmt::format(
  //   "sqlite3 {} '.mode csv' '.separator {}' '.import --skip 1 {}/{} {}'",
  //   this->filename,
  //   std::string{seperator},
  //   outDir,
  //   file,
  //   dbname
  // );
  SPDLOG_INFO("running: {}", cmd);
  system(cmd.c_str());
  
  int count = db(select(sqlpp::count(1)).from(trees).unconditionally()).front().count;

}

void TreesApi::export_csv(const std::string& file, const std::string& dbname, char seperator) {
  std::string cmd = "sqlite3 -header -csv -separator '" + std::string{seperator} + + "' " + this->filename + " 'select * from " + dbname + ";' > " + outDir + "/" + file;
  // std::string cmd = fmt::format(
  //   "sqlite3 -header -csv -separator '{}' {} 'select * from {};' > {}/{}",
  //   std::string{seperator},
  //   this->filename,
  //   dbname,
  //   outDir,
  //   file
  // );
  SPDLOG_INFO("running: {}", cmd);
  system(cmd.c_str());
}

void TreesApi::reset_trees(label_size_t labelSize) {
  std::string name = trees::Trees::_alias_t::_literal;

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
  std::vector<Tree> out;

  auto select_stmt = db.prepare(select(all_of(trees)).from(trees).where(trees.labelSize == labelSize));

  for (auto& row : db(select_stmt)) {
    std::vector<code_t> branches = json::parse(row.branches.text).get<std::vector<code_t>>();
    std::vector<degree_t> degrees = json::parse(row.degrees.text).get<std::vector<degree_t>>();
    Tree new_tree(row.id.value(), branches, row.labelSize.value(), degrees);

    out.push_back(new_tree);
  }

  return out;
}

int TreesApi::insert_tree(const Tree& t) {
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


  return 0;
}

int TreesApi::insert_trees(const std::vector<Tree>& tr, label_size_t N) {

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
      std::cout << "\r[insert_trees]" << (N ? " N = " + std::to_string(N) : " ") << " batch " << i / CHUNK_SIZE + 1
                << " saved" << std::flush;
    } catch (const std::exception& e) {
      std::cerr << e.what() << std::endl;
      return 1;
    }
  }
  std::cout << std::endl;


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