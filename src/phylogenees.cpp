#include "phylogenees.h"

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

int make_trees(label_size_t N, APIWrapper& db, code_t IMAX, code_t IMIN) {

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
    label_size_t right_tree_size = bit_length(J) + 1;
    code_t right_target = J + elt_N;

    // Grab size for the rest of the partition;
    label_size_t left_tree_size = N - right_tree_size;
    code_t left_target = set_1toN - right_target;

    std::vector<Tree> right_trees = db.get_trees(right_tree_size);
    std::vector<Tree> left_trees = db.get_trees(left_tree_size);

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

        if (left_tree_size > 1) {
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