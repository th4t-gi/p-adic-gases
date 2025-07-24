
#include <spdlog/fmt/chrono.h>
#include <spdlog/spdlog.h>
#include <spdlog/stopwatch.h>

#include <boost/program_options.hpp>
#include <iostream>
#include <map>

#include "api.h"
#include "logger.h"
#include "tree.h"

#include <algorithm>

namespace po = boost::program_options;

bool check_tree(const Tree fork, code_t I_max, code_t I_min){
  int m = std::min(bit_length(I_max),bit_length(I_min));
  for (auto J : fork.branches){
    if (bit_length(J) == 2){
      if((J & I_max) && (J & I_min)){
        m--;
      }
    }
  }
  return (m == 0);
}


void make_chains(label_size_t N, std::vector<std::vector<Tree>>& local, code_t IMAX, code_t IMIN) {
  double sum_of_prob = 0;
  int p = 2;
  // base cases for 1, 2
  if (N <= 2) {
    switch (N) {
      case 1: {
        Tree one{std::vector<code_t>{}, 1, std::vector<degree_t>{}};
        local[N - 1].push_back(one);
        // trees::insert_tree(db, one);
        break;
      }

      case 2: {
        Tree two{std::vector<code_t>{3}, 2, std::vector<degree_t>{2}};
        local[N - 1].push_back(two);
        // trees::insert_tree(db, two);
        break;
      }

      default:
        break;
    }
    return;
  }

  code_t set_1toN = (1 << N) - 1;
  code_t elt_N = (1 << (N - 1));

  Tree base_fork;
  base_fork.branches.push_back(set_1toN);
  base_fork.setSize = N;

  // iterate over all subsets of {1,2,..., N-1} that have N-2 or fewer elements
  for (code_t J = 0; J < elt_N - 1; J++) {
    Tree curr_fork = base_fork;
    // Grab number of bits in J and add it to the number of bits in N_max
    label_size_t right_chain_size = bit_length(J) + 1;
    code_t right_target = J + elt_N;

    // Grab size for the rest of the partition;
    label_size_t left_chain_size = N - right_chain_size;
    code_t left_target = set_1toN - right_target;

    // Move through all trees with J (buddies) unioned with {N}
    for (Tree right_fork : local[right_chain_size - 1]) {
      // shifts branches for the first of the nested calls.
      Tree right_translated_fork = right_fork.translate(right_target);

      // Look at other side of the partition
      for (Tree left_fork : local[left_chain_size - 1]) {
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
        //Check if fork is a prevailing fork
        if(check_tree(curr_fork, IMAX, IMIN)){
          //PUSH TREE TO R*_I Vector
        }

        local[N - 1].push_back(curr_fork);
        // Probabilities
        printf("The fork: %s\n", curr_fork.to_string().c_str());
        printf("has probability %lf, with prime %d\n", curr_fork.probability(p), p);
        sum_of_prob += curr_fork.probability(p);
        // trees::insert_tree(db, curr_fork);

        if (left_chain_size > 1) {
          dup_fork.append(left_translated_fork, false);
          dup_fork.degrees.insert(dup_fork.degrees.begin(), 2);
          // trees::insert_tree(db, dup_fork);

          //Check if fork is a prevailing fork
          if(check_tree(curr_fork, IMAX, IMIN)){
          //PUSH TREE TO R*_I Vector
          }

          local[N - 1].push_back(dup_fork);

          // Probabilities
          printf("The fork: %s\n", dup_fork.to_string().c_str());
          printf("has probability %lf, with prime %d\n", dup_fork.probability(p), p);
          sum_of_prob += dup_fork.probability(p);
        }

        // Reset the current fork inside the for loop
        curr_fork = base_fork;
      }
    }
  }

  printf("The sume of the probabilities is %lf\n", sum_of_prob);
  return;
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
        ("ignore_change", "Do not ask what the changes/goal of this run is")
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
  if (!vm.count("ignore_change")) {
    std::cout << "What changes would you like to record? ";
    std::getline(std::cin, change);
  }

  logger::preamble(concat_argv(argc, argv), change);

  // intialize database connection
  TreesApi db(db_file, true);

  bool print = vm.count("print-trees");
  // Start the clock
  spdlog::stopwatch sw;

  // import from csv
  if (!import_file.empty()) {
    db.import_csv(import_file, "trees");
    SPDLOG_INFO("{}s", sw);
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
      db.export_csv(export_file);
      SPDLOG_INFO("[export] ({:.4f}s)", sw);
    }

    return 0;
  }

  sw.reset();

  // caching trees
  std::vector<std::vector<Tree>> tree_arr;
  tree_arr.reserve(N);
  for (int k = 1; k <= N; k++) {
    std::vector<Tree> v = db.get_trees(k);
    if (v.size()) {
      tree_arr.push_back(v);
    } else {
      tree_arr.push_back(std::vector<Tree>{});
    }
  }

  SPDLOG_INFO("cached trees successfully ({:.4f}s)", sw);

  char ready = question("ready to run calculation? (y/n) ", 'y');

  if (ready == 'n') {
    SPDLOG_INFO("cancelling calculation");
    return 0;
  } else if (ready == 'y') {
    // MAIN LOGIC
    SPDLOG_INFO("Generating trees for all label sizes " + std::to_string(max) + " to " + std::to_string(N) + "...");

    sw.reset();
    spdlog::stopwatch total;

    // compute chains for size max + 1 to N and store in tree_arr
    for (int i = max + 1; i <= N; i++) {
      SPDLOG_INFO("calculating N = {}", i);
      make_chains(i, tree_arr, IMAX, IMIN);

      SPDLOG_DEBUG("computed {} trees", tree_arr[i - 1].size());
      if (print) {
        for (Tree t : tree_arr[i - 1]) {
          std::cout << t.to_string() << std::endl;
        }
      }
    }

    SPDLOG_INFO("finished computation ({:.4f}s)", sw);
    sw.reset();

    // Writing to filesystem
    SPDLOG_INFO("saving to {}", db.filename);
    for (int i = max + 1; i <= N; i++) {
      SPDLOG_DEBUG("starting N = {}", i);
      db.insert_trees(tree_arr[i - 1], i);
    }

    SPDLOG_INFO("finished write ({:.4f}s)", sw);
    sw.reset();

    if (!export_file.empty()) {
      SPDLOG_INFO("exporting to {}", export_file);
      db.export_csv(export_file);
      SPDLOG_INFO("finished export ({:.4f}s)", sw);
    }

    SPDLOG_INFO("total time elapsed: {:.4f}s", total);
  }

  return 0;
}