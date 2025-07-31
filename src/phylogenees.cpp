
#include <spdlog/fmt/chrono.h>
#include <spdlog/spdlog.h>
#include <spdlog/stopwatch.h>

#include <boost/program_options.hpp>
#include <iostream>
#include <map>

#include "api.h"
#include "logger.h"
#include "tree.h"

namespace po = boost::program_options;

bool check_tree(const Tree fork, code_t I_max, code_t I_min) {
  int m = std::min(bit_length(I_max), bit_length(I_min));
  for (auto J : fork.branches) {
    if (bit_length(J) == 2) {
      if ((J & I_max) && (J & I_min)) {
        m--;
      }
    }
  }
  return (m == 0);
}

int make_chains(label_size_t N, APIWrapper& db, code_t IMAX, code_t IMIN) {

  std::vector<Tree> local;
  int total = 0;
  local.reserve(2 * db.BATCH_WRITE_SIZE);

  // base cases for N=1 or N=2
  if (N == 1) {
    Tree one{{}, 1, {}};
    db.insert_tree(one);
    return 1;
  } else if (N == 2) {
    Tree two{{3}, 2, {2}};
    db.insert_tree(two);
    return 1;
  }

  code_t set_1toN = (1 << N) - 1;
  code_t elt_N = (1 << (N - 1));

  const Tree base_fork({set_1toN}, N);

  // iterate over all subsets of {1,2,..., N-1} that have N-2 or fewer elements
  for (code_t J = 0; J < elt_N - 1; ++J) {
    Tree curr_fork = base_fork;
    // Grab number of bits in J and add it to the number of bits in N_max
    label_size_t right_chain_size = bit_length(J) + 1;
    code_t right_target = J + elt_N;

    // Grab size for the rest of the partition;
    label_size_t left_chain_size = N - right_chain_size;
    code_t left_target = set_1toN - right_target;

    std::vector<Tree> right_trees = db.get_trees(right_chain_size);
    std::vector<Tree> left_trees = db.get_trees(left_chain_size);

    for (Tree right_fork : right_trees) {
      // shifts branches for the first of the nested calls.
      Tree right_translated_fork = right_fork.translate(right_target);

      // Look at other side of the partition
      for (Tree left_fork : left_trees) {
        curr_fork.append(right_translated_fork);
        // shifts branches for the second of the nested calls.
        Tree left_translated_fork = left_fork.translate(left_target);

        Tree dup_fork = curr_fork;
        // Saving the two possible trees to DB
        curr_fork.append(left_translated_fork, true);
        if (left_translated_fork.degrees.size()) {
          curr_fork.degrees.insert(curr_fork.degrees.begin(), 1 + left_translated_fork.degrees.front());
        } else {
          curr_fork.degrees.insert(curr_fork.degrees.begin(), 2);
        }
        // Check if fork is a prevailing fork
        if (check_tree(curr_fork, IMAX, IMIN)) {
          // PUSH TREE TO R*_I Vector
        }

        local.push_back(curr_fork);

        if (left_chain_size > 1) {
          dup_fork.append(left_translated_fork, false);
          dup_fork.degrees.insert(dup_fork.degrees.begin(), 2);

          // Check if fork is a prevailing fork
          if (check_tree(curr_fork, IMAX, IMIN)) {
            // PUSH TREE TO R*_I Vector
          }

          local.push_back(dup_fork);
        }

        // Reset the current fork inside the for loop
        curr_fork = base_fork;
      }

      // SPDLOG_WARN("local has {} trees", local.size());

      if (local.size() >= db.BATCH_COMPUTE_SIZE) {
        // SPDLOG_INFO("local has {} trees", local.size());
        total += db.insert_trees(local, N);
        local.clear();
      }
    }
  }

  total += db.insert_trees(local, N);

  SPDLOG_INFO("computed {} trees in total", total);
  return total;
}


int main(int argc, char** argv) {
  code_t N;
  std::string import_file = "";
  std::string export_file = "";
  std::string db_file = "trees.db";
  int reset_to;
  code_t IMAX = 0;
  code_t IMIN = 0;
  // Declaring arguments
  po::options_description desc("Allowed options");
  desc.add_options()
        ("help", "produce help message")
        ("n-value,n", po::value<code_t>(&N)->required(), "Number of particles")
        ("reset,r", po::value<int>(&reset_to),"Reset database to kth size")
        ("create_ri", "Create the full database")
        ("i_max", po::value<code_t>(&IMAX), "Indices with maximum charge")
        ("i_min", po::value<code_t>(&IMIN), "Indices with minimum charge")
        ("print-trees,p", "Do you want to print trees?")
        ("import", po::value<std::string>(&import_file), "Imported database")
        ("export", po::value<std::string>(&export_file), "Exported database")
        ("database,d", po::value<std::string>(&db_file), "database file")
        ("ignore-changes", "Do not ask what the changes/goal of this run is")
        ("verbose,v", "Do verbose or not");

  po::positional_options_description p;
  p.add("n-value", 1);

  po::variables_map vm;

  try {
    po::store(po::command_line_parser(argc, argv).options(desc).positional(p).run(), vm);
    po::store(po::parse_command_line(argc, argv, desc), vm);

    if (vm.count("help")) {
      std::cout << desc << std::endl;
      return 0;
    }

    po::notify(vm);
  } catch (const po::error& e) {
    std::cerr << "Error parsing options: " << e.what() << std::endl;
    return 1;
  }

  // intialize logger
  logger::init("log", vm.count("verbose") ? spdlog::level::debug : spdlog::level::info);

  std::string change = "";
  if (!vm.count("ignore-changes")) {
    std::cout << "What changes would you like to record? ";
    std::getline(std::cin, change);
  }

  logger::preamble(concat_argv(argc, argv), change);

  // intialize database connection
  APIWrapper db(db_file, true);

  bool print = vm.count("print-trees");
  // Start the clock
  spdlog::stopwatch sw;

  // import from csv
  if (!import_file.empty()) {
    // db.import_csv(import_file, "trees");
    SPDLOG_INFO("IMPORT IS CURRENTLY DISABLED {}s", sw);
    return 0;
  }

  sw.reset();

  // reset
  if (vm.count("reset") && (N > reset_to)) {
    db.reset_trees(reset_to);
    SPDLOG_INFO("reset successfully ({:.4f}s)", sw);
  }

  sw.reset();

  // calculate if N is less than max
  int max = db.get_max_label_size();

  if (max >= N) {
    SPDLOG_WARN("already generated trees up to N = " + std::to_string(N) + " (max = " + std::to_string(max) + ")");

    if (!export_file.empty()) {
      // db.export_csv(export_file);
      SPDLOG_INFO("EXPORT IS CURRENTLY DISABLED [export] ({:.4f}s)", sw);
    }

    return 0;
  }

  sw.reset();

  // caching trees
  // std::vector<std::vector<Tree>> tree_arr;
  // tree_arr.reserve(N);
  // for (int k = 1; k <= N; k++) {
  //   std::vector<Tree> v = db.get_trees(k, false);

  //   if (v.size()) {
  //     tree_arr.push_back(v);
  //   } else {
  //     tree_arr.push_back(std::vector<Tree>{});
  //   }
  // }

  // SPDLOG_INFO("cached trees successfully ({:.4f}s)", sw);

  char ready = question("ready to run calculation? (y/n) ", 'y');

  if (ready == 'n') {
    SPDLOG_INFO("cancelling calculation");
    return 0;
  } else if (ready == 'y') {
    // MAIN LOGIC
    SPDLOG_INFO("Generating trees for label sizes {} to {}...", std::to_string(max + 1), std::to_string(N));

    sw.reset();
    spdlog::stopwatch total;

    // compute chains for size max + 1 to N and store in tree_arr
    for (int i = max + 1; i <= N; i++) {
      SPDLOG_INFO("calculating N = {}", i);
      int trees_num = make_chains(i, db, IMAX, IMIN);

      if (print) {
        for (Tree t : db.get_trees(i)) {
          std::cout << t.to_string() << std::endl;
        }
      }
    }

    SPDLOG_INFO("finished computation ({:.4f}s)", sw);
    sw.reset();

    // Writing to filesystem
    // SPDLOG_INFO("saving to {}", db.getDBpath());
    // for (int i = max + 1; i <= N; i++) {
    //   SPDLOG_DEBUG("starting N = {}", i);
    //   db.insert_trees(tree_arr[i - 1], i, false);
    // }

    // SPDLOG_INFO("finished write ({:.4f}s)", sw);
    // sw.reset();

    if (!export_file.empty()) {
      SPDLOG_INFO("EXPORT IS CURRENTLY DISABLED exporting to {}", export_file);
      // db.export_csv(export_file);
      SPDLOG_INFO("finished export ({:.4f}s)", sw);
    }

    SPDLOG_INFO("total time elapsed: {:.4f}s", total);
  }

  return 0;
}