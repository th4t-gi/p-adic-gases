#include <iostream>
#include <map>
#include "api.h"
#include "tree.h"

void make_chains(sqlpp::sqlite3::connection& db, unsigned int N) {

  //base cases for 0, 1, 2
  if (N <= 2) {
    switch (N) {
      // case 0:{
      //   Tree empty{std::vector<unsigned int>{}, 0};
      //   trees::insert_tree(db, empty);
      //   break;
      // }
      
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
    return;
  }

  code set_1toN = (1 << N) - 1;
  code elt_N = (1 << (N-1));

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
        
        //Saving the two possible trees to DB
        curr_fork.append(translated_fork_2, true);
        trees::insert_tree(db, curr_fork);

        //TODO figure out better way to append
        if (chain_size_2 > 1) {
          curr_fork.branches.insert(curr_fork.branches.begin() + 1, target_2);
          trees::insert_tree(db, curr_fork);
        }

        //Reset the current fork inside the for loop
        curr_fork=base_fork;
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
 
  for (int i = 1; i <= 5; i++){
    make_chains(db, i);
    
    for (Tree t : trees::get_trees(db, i)) {
      std::cout << t.to_set_string() << std::endl;
    }
  }

  // for (int i = 0; i <= n; i++) {
  //   printf("%d: %d\n", i, phylogenees_num(i));
  // }

  return 0;
}