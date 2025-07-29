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
  std::string tbl_name = get_tree_table(labelSize, is_filtered);
  Tree t;

  if (db.tableExists(tbl_name)) {
    std::string stmt = std::format("SELECT * FROM {} WHERE rowid == {}", tbl_name, treeId);
    SQLite::Statement query(db, stmt);

    query.executeStep();
    t = Tree::fromColumns(query.getColumn(0), query.getColumn(1), query.getColumn(2), query.getColumn(3));
  }
  return t;
}

std::vector<Tree> APIWrapper::get_trees(label_size_t labelSize, bool is_filtered) {
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

  std::string tbl_name = get_tree_table(labelSize, is_filtered);
  if (!db.tableExists(tbl_name)) {
    create_tree_table(labelSize, is_filtered);
  }

  static constexpr size_t CHUNK_SIZE = 100000;

  db.exec("PRAGMA synchronous = OFF");
  db.exec("PRAGMA journal_mode = MEMORY");

  for (int i = 0; i < trees.size(); i += CHUNK_SIZE) {
    // START BATCH TRANSACTION
    SQLite::Transaction transaction(db);

    std::string stmt = std::format("INSERT INTO {} VALUES (?, ?)", tbl_name);
    SQLite::Statement query(db, stmt);

    for (int j = i; j < i + CHUNK_SIZE && j < trees.size(); ++j) {
      // insert individual tree
      const Tree& t = trees[j];

      // query.bind(1, (int64_t)t.id);
      query.bind(1, vectorToJsonString(t.branches));
      query.bind(2, vectorToJsonString(t.degrees));

      try {
        query.exec();
        query.reset();
        std::cout << "\r[insert_trees]" << (labelSize ? " N = " + std::to_string(labelSize) : " ") << " batch "
                  << i / CHUNK_SIZE + 1 << " saved" << std::flush;
      } catch (const std::exception& e) {
        std::cerr << e.what() << std::endl;

        return 1;
      }
    }
    transaction.commit();
    // FINISH BATCH TRANSACTION
  }
  std::cout << std::endl;
  db.exec("PRAGMA synchronous = FULL");


  return 0;
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

void APIWrapper::import_csv(const std::string& file, const std::string& tablename, char seperator) {
  std::string cmd = std::format(
    "sqlite3 {} '.mode csv' '.separator {}' '.import --skip 1 {}/{} {}'",
    dbpath,
    std::string{seperator},
    outDir,
    file,
    tablename
  );
  SPDLOG_INFO("running: {}", cmd);
  system(cmd.c_str());

  // int count = db(select(sqlpp::count(1)).from(treesTable).unconditionally()).front().count;

  // SPDLOG_INFO("Imported {} rows", count);
}

void APIWrapper::export_csv(const std::string& file, const std::string& tablename, char seperator) {
  std::string cmd = std::format(
    "sqlite3 -header -csv -separator '{}' {} 'select * from {};' > {}/{}",
    std::string{seperator},
    dbpath,
    tablename,
    outDir,
    file
  );
  SPDLOG_INFO("running: {}", cmd);
  system(cmd.c_str());
  SPDLOG_INFO("exported to {}", file);
}