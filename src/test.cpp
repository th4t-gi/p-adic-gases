//
// #include <sqlpp11/sqlite3/connection.h>

// #include <cstdlib>
#include <fmt/format.h>
#include <spdlog/logger.h>
#include <spdlog/sinks/basic_file_sink.h>
#include <spdlog/sinks/dup_filter_sink.h>
#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/spdlog.h>

// #include <boost/program_options.hpp>
// #include <memory>
#include <SQLiteCpp/Database.h>

// #include "logger.h"
#include "utils.h"
#include "api.h"
#include "tree.h"

#define COLS 3

namespace test {
int hello();
void show_progress(int percentage);
}  // namespace test

class TestObj {
 public:
  int64_t id;
  std::string info;
  std::string info2;
  std::vector<double> probs;
  inline static constexpr std::array<int, 5> primes = {2, 3, 5, 7, 11};
  std::vector<std::string> names = {"id", "info", "info2"};

  template <typename... Args>
  TestObj(int64_t id, const char* info, const char* info2, Args&&... probs)
      : id{id}, info{info}, info2{info2}, probs{static_cast<double>(probs)...} {
    for (int p : primes) {
      names.push_back(fmt::format("probs{:d}", p));
    }
  }

  void print() {
    std::cout << id << " " << info << "\n";

    for (double p : probs) {
      std::cout << p << ",";
    }
    std::cout << std::endl;
  }

  constexpr std::string getColsString() {
    std::string s = "(";
    for (size_t i = 0; i < names.size(); ++i) {
      if (i > 0) s += ", ";
      s += names.at(i);
    }
    s += ")";
    return s;
  }

  constexpr std::string getValuesString() {
    std::string valuesStr = "(";
    for (size_t i = 0; i < names.size(); ++i) {
      if (i > 0) valuesStr += ", ";
      valuesStr += "?";
    }
    valuesStr += ")";
    return valuesStr;
  }

  void insert_testobj(SQLite::Database& db, const std::string& tableName) {
    std::string sql = fmt::format("INSERT INTO {} {} VALUES {};", tableName, getColsString(), getValuesString());

    // fmt::print("sql: {}", sql);

    SQLite::Statement query(db, sql);

    printf("%s\n", query.getExpandedSQL().c_str());
    int idx = 1;
    query.bind(idx++, id);
    query.bind(idx++, info);
    query.bind(idx++, info2);
    for (double p : probs) {
      query.bind(idx++, p);
    }

    printf("%s\n", query.getExpandedSQL().c_str());

    query.exec();
  }
};

int main(void) {
  // system("sqlite3 -header -csv trees.db 'select * from blocks where set_size = 3;' > test.csv");

  // ApiWrapper db{"test2.db", true};

  // // db.reset_trees(0);
  // db.import_csv("test4.csv");

  // int max = db.get_max_label_size();
  // for (int i = 0; i <= max; i++) {
  //   for (Tree t : db.get_trees(i)) {
  //     std::cout << t.id << " " << t.to_set_string() << std::endl;
  //   }
  // }
  // for (int i = 0; i < trees.size(); i+= 1400) {
  //   auto t = trees[i];
  //   std::cout << t.to_string(false) << "\n" << t.to_string(true) << "\n" << std::endl;
  // }

  // Tree t{std::vector<code_t>{3}, 2, std::vector<degree_t>{2}};
  // Tree t2{std::vector<code_t>{15,7,6}, 4, std::vector<degree_t>{2,2,2}};

  // std::cout << t.to_string() << std::endl;
  // std::cout << t2.to_string() << std::endl;

  // api.import_csv("out/out1to5.csv", "trees");

  // for (auto& tree : api.get_trees(5)) {
  //   std::cout << tree.to_string() << std::endl;
  // }

  // api.export_csv("out1to5.csv", "trees");

  // unsigned long max = std::numeric_limits<int>::max() >> 8;
  // std::cout << max << std::endl;

  APIWrapper api("./test.db", false);

  SQLite::Statement query(api.db, "SELECT * FROM trees WHERE label_size == 6");

  std::vector<Tree> objs;
  while (query.executeStep()) {
    Tree obj = Tree::fromColumns(
      query.getColumn(0),
      query.getColumn(1),
      query.getColumn(2),
      query.getColumn(3)
    );
    std::cout << obj.to_string() << "\n";
    objs.push_back(obj);
  }
  std::cout << std::endl;

  // std::cout << std::endl;

  // for (TestObj o : objs) {
  //   o.print();
  // }

  // TestObj obj2{6, "nop", "opq"};

  // obj2.insert_testobj(db, "core2");

  return 0;
}



namespace test {
int hello() {
  SPDLOG_TRACE("this is a trace");
  SPDLOG_DEBUG("this is a debug");
  SPDLOG_INFO("this is info");
  SPDLOG_WARN("this is a warning");
  SPDLOG_ERROR("this is an error");
  SPDLOG_CRITICAL("this is critical");

  return 0;
}

// Function to display progress bar directly to stdout
void show_progress(int percentage) {
  int barWidth = 50;
  int pos = barWidth * percentage / 100;

  std::cout << "\r[";
  for (int i = 0; i < barWidth; ++i) {
    if (i < pos)
      std::cout << "=";
    else if (i == pos)
      std::cout << ">";
    else
      std::cout << " ";
  }
  std::cout << "] " << std::setw(3) << percentage << "%" << std::flush;
}
}  // namespace test
