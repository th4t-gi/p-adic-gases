#include <iostream>
#include <map>
#include "api.h"

typedef unsigned int code;

void make_chains(sqlpp::sqlite3::connection& db, unsigned int N) {

  //TODO: case if N is 0;
  if (N <= 2) {
    switch (N) {
      case 0:{
        Tree empty{std::vector<unsigned int>{}, 0};
        trees::insert_tree(db, empty);
        break;
      }
      
      case 1: {
        Tree one{std::vector<unsigned int>{}, 1};
        trees::insert_tree(db, one);
        break;
      }
      
      case 2: {
        Tree two{std::vector<unsigned int>{3}, 2};
        trees::insert_tree(db, two);
        break;
      }

      default:
        break;
    }
  }

  code set_1toN = (1 << N) - 1;
  code elt_N = (1 << (N-1));

  Tree base_fork;
  base_fork.branches.push_back(set_1toN);
  
  Tree curr_fork = base_fork;

  // The case where there is only a singleton left when we combine the last
  // element and all of its buddies.
  for (int j = 1; j < N; j++) {
    // Move through all the singletons
    //make labelset {1, 2, ... ,j-1, j+1, ... N}
    unsigned target = (1 << N) - (1 << j);
    // Gets trees for {1,2,...N-1}
    for (Tree fork0 :/*\in*/ trees::get_trees(db, N-1)) {
      // Shifts the branches
      std::vector<code> shifted_branches_0{};
      for (auto block : fork0.branches) {
        shifted_branches_0.push_back(translate_block_std(target, block));
      }

      curr_fork.branches.insert(curr_fork.branches.end(), shifted_branches_0.begin(), shifted_branches_0.end());
      //Save fork to db. NEED TO COMPLETE
      trees::insert_tree(db, curr_fork);
    }
  }

  // The main case where the buddies of the last element is the set of J
  for (code J = 0; J < elt_N; J++) {
    // Grab number of bits in J and add it to the number of bits in N_max
    int chain_size_1 = bit_length(J) + 1;
    code target_1 = J + elt_N;

    // Move through all trees of the designated size
    for (Tree fork1 : trees::get_trees(db, chain_size_1)) {

      // shifts branches for the first of the nested calls.
      std::vector<int> shifted_branches{};
      for (auto block : fork1.branches) {
        shifted_branches.push_back(translate_block_std(target_1, block));
      }
      // Current Tree inherits all branches
      curr_fork.branches.insert(curr_fork.branches.end(), shifted_branches.begin(), shifted_branches.end());

      // Grab size for the rest of the partition;
      int chain_size_2 = N - chain_size_1;
      code target_2 = set_1toN - target_1;
      // Look at other side of the partition
      for (auto fork2 : trees::get_trees(db, chain_size_2)) {
        // shifts branches for the second of the nested calls.
        std::vector<int> shifted_branches_2{};
        for (auto block2 : fork2.branches) {
          shifted_branches_2.push_back(translate_block_std(target_2, block2));
        }

        // Two choices
        // // Remove the 'top' branch
        // auto ne = std::remove(shifted_branches_2.begin(), shifted_branches_2.end(), N - I_max - J); 
        // shifted_branches_2.erase(ne, shifted_branches_2.end());
        // // 2) Current tree inherits the branchs
        curr_fork.branches.insert(curr_fork.branches.end(), shifted_branches_2.begin()+1, shifted_branches_2.end());
        //save tree to db
        trees::insert_tree(db, curr_fork);
        // OR
        // 1) Current Tree inherits all branches
        // curr_fork.branches.insert(curr_fork.branches.end(), shifted_branches_2.begin(), shifted_branches_2.end());
        curr_fork.branches.push_back(target_2);
        //save tree to db
        trees::insert_tree(db, curr_fork);
      }
    }
  }
  return;
}

int main(void) {

  sqlpp::sqlite3::connection_config config;
  config.path_to_database = "trees.db";
  config.flags = SQLITE_OPEN_READWRITE;


  trees::Trees trees;
  sqlpp::sqlite3::connection db(config);

  make_chains(db, 4);

  // for (int i = 0; i <= n; i++) {
  //   printf("%d: %d\n", i, phylogenees_num(i));
  // }

  return 0;
}