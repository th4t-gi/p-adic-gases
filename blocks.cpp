#include <iostream>
#include <bitset>
#include <vector>
#include <string>
#include <sqlpp11/sqlite3/connection.h>
#include "trees.h"
#include "api.h"

std::string binarySet(unsigned n, int width) {
    std::string result = "{";
    bool comma = false;

    for (int i = 0; i < width; ++i) {
        if (n & (1 << i)) {
            if (comma) result += ",";
            result += std::to_string(i + 1);  // 1-based indexing
            comma = true;
        }
    }
    result += "}";
    return result;
}

int main() {
    const unsigned int N = (1ULL << 12);
    const int width = 31 - std::countl_zero(N);//bitwise for log_2(n)
  

    sqlpp::sqlite3::connection_config config;
    config.path_to_database = "trees.db";
    config.flags = SQLITE_OPEN_READWRITE;


    trees::Blocks table;
    sqlpp::sqlite3::connection db(config);

    std::cout << "Id\tBin\tSet\t\tSize\n";
    for (int i = 0; i < N; ++i) {
        std::bitset<width> b(i);
        std::string setStr = binarySet(i, width);
        int setSize = b.count();
        if (!trees::insert_block(db, i, setStr, setSize)) {
            std::cout << i << "\t" << b << "\t" << setStr;
            if (setStr.size() < 8) std::cout << "\t"; // for alignment
            std::cout << "\t" << setSize << "\n";
        }
        
    }

    return 0;
}