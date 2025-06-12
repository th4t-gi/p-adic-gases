#include <iostream>
#include <map>

#include "api.h"
#include "tree.h"

void make_chains(sqlpp::sqlite3::connection& db, code N) {
  // base cases for 0, 1, 2
  if (N <= 2) {
    switch (N) {
        // case 0:{
        //   Tree empty{std::vector<unsigned int>{}, 0};
        //   trees::insert_tree(db, empty);
        //   break;
        // }

      case 1: {
        Tree one{std::vector<code>{}, 1, std::vector<int>{}};
        trees::insert_tree(db, one);
        break;
      }

      case 2: {
        Tree two{std::vector<code>{3}, 2, std::vector<int>{2}};
        trees::insert_tree(db, two);
        break;
      }

      default:
        break;
    }
    return;
  }

  code set_1toN = (1 << N) - 1;
  code elt_N = (1 << (N - 1));

  Tree base_fork;
  base_fork.branches.push_back(set_1toN);
  base_fork.setSize = N;

  // iterate over all subsets of {1,2,..., N-1} that have N-2 or fewer elements
  for (code J = 0; J < elt_N - 1; J++) {
    Tree curr_fork = base_fork;
    // Grab number of bits in J and add it to the number of bits in N_max
    int chain_size_1 = bit_length(J) + 1;
    code target_1 = J + elt_N;

    // Grab size for the rest of the partition;
    int chain_size_2 = N - chain_size_1;
    code target_2 = set_1toN - target_1;

    // Move through all trees with J (buddies) unioned with {N}
    for (Tree fork1 : trees::get_trees(db, chain_size_1)) {
      // shifts branches for the first of the nested calls.
      Tree translated_fork_1 = fork1.translate(target_1);
      curr_fork.append(translated_fork_1);

      // Look at other side of the partition
      for (auto fork2 : trees::get_trees(db, chain_size_2)) {
        // shifts branches for the second of the nested calls.
        Tree translated_fork_2 = fork2.translate(target_2);

        Tree dup_fork = curr_fork;
        // Saving the two possible trees to DB
        curr_fork.append(translated_fork_2, true);
        if (translated_fork_2.degrees.size()) {
          curr_fork.degrees.insert(curr_fork.degrees.begin(), 1 + translated_fork_2.degrees.front());
        } else {
          curr_fork.degrees.insert(curr_fork.degrees.begin(), 2);
        }
        trees::insert_tree(db, curr_fork);

        if (chain_size_2 > 1) {
          dup_fork.append(translated_fork_2, false);
          dup_fork.degrees.insert(dup_fork.degrees.begin(), 2);
          trees::insert_tree(db, dup_fork);
        }

        // Reset the current fork inside the for loop
        curr_fork = base_fork;
      }
    }
  }
  return;
}

int reset(connection& db) {
  char response = question("Do you want to reset? (y/n) ", 'n');
  if (response == 'n') {
    std::cout << "cancelling reset.." << std::endl;
    return 1;
  }

  int size = question("what sizes do you want to save (put 0 for nothing)? ", 0);

  trees::reset_trees(db, size);

  std::cout << "reseted successfully" << std::endl;
  return 0;
}

int main(void) {
  // intialize database connection
  sqlpp::sqlite3::connection_config config;
  config.path_to_database = "trees.db";
  config.flags = SQLITE_OPEN_READWRITE;

  trees::Trees trees;
  sqlpp::sqlite3::connection db(config);
  db.execute("PRAGMA busy_timeout = 5000;");

  code N = question("what should N equal? ", 3);

  // calculate reset and quit if N is less than what we deleted
  int did_reset = !reset(db);
  int max = trees::get_max_label_size(db);

  if (max >= N) {
    std::cout << "already generated trees up to N = " + std::to_string(N) + " (max = " + std::to_string(max) + ")"
              << std::endl;
    return 0;
  }

  // more config (for printing and confirmation)
  char print = question("Do you want to print out the trees? (y/_n_) ", 'n');
  char ready = question("ready to run calculation? (_y_/n)", 'y');
  if (ready == 'n') {
    std::cout << "cancelling calculation" << std::endl;
    return 0;
  } else if (ready == 'y') {
    // MAIN LOGIC
    std::cout << "Generating trees for all label sizes between " + std::to_string(max) + " and " + std::to_string(N) +
                   "..."
              << std::endl;

    //Start the clock
    auto start = std::chrono::steady_clock::now();

    for (int i = max + 1; i <= N; i++) {
      std::cout << "beginning make_chains(N = " + std::to_string(i) + ")" << std::endl;
      make_chains(db, i);

      if (print == 'y') {
        for (Tree t : trees::get_trees(db, i)) {
          std::cout << t.to_set_string() << std::endl;
        }
      }
    }

    auto end = std::chrono::steady_clock::now();
    auto diff = end - start;

    double duration = std::chrono::duration<double, std::milli>(diff).count() / 1000.0;

    std::cout << duration << "s" << std::endl;

    
  }

  // for (int i = 0; i <= n; i++) {
  //   printf("%d: %d\n", i, phylogenees_num(i));
  // }

  return 0;
}