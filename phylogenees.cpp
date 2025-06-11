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
    return;
  }

  code set_1toN = (1 << N) - 1;
  code elt_N = (1 << (N-1));

  Tree base_fork;
  base_fork.branches.push_back(set_1toN);
  base_fork.setSize = N;

  //Insert the base fork
  trees::insert_tree(db, base_fork);
  
  // The case where there is only a singleton left when we combine the last
  // element and all of its buddies.

    for (int j = 1; j < N; j++) {
      Tree curr_fork = base_fork;
      // Move through all the singletons
      //make labelset {1, 2, ... ,j-1, j+1, ... N}
      unsigned target = (1 << N) - (1 << (j-1)) - 1; // Target is not working the correct way this may be a fix?
      // Gets trees for {1,2,...N-1}

      for (Tree fork0 : trees::get_trees(db, N-1)) {
        // Shifts the branches

        //Checking that blocks in the fork. Each time we run through this block the first entry is the same, leading to the repetition in the table.
        /*printf("Blocks in fork 0:\n");
        for(auto blocks : fork0.branches){
          printf("%d,", blocks);
        }
        printf("\n");*/
        std::vector<code> shifted_branches_0{};
        for (auto block : fork0.branches) {
          //printf("j = %d, target = %d, block is %d, translated block is %llu\n",j, target, block, translate_block_std(target, block)); //DEBUGGING HELPER
          
          
          shifted_branches_0.push_back(translate_block_std(target, block));
          curr_fork.branches.insert(curr_fork.branches.end(), shifted_branches_0.begin(), shifted_branches_0.end());
         
          //Printing the current branch we are saving to the tree
          /*printf("Saving the branch:\n");
          for(auto block : curr_fork.branches){
            printf("%d,", block);
          }
          printf("\n");
          */

          //Saving to tree inside the for loop over fork0.branches instead of outside to avoid repetition
          trees::insert_tree(db, curr_fork);
          //Resetting within the for loop to avoid unwanted repettion
          curr_fork=base_fork;
        }
      }
    }

  //This case should not run when N is less that 3. 
  
  // The main case where the buddies of the last element is the set of J
    for (code J = 0; J < elt_N; J++) {
      Tree curr_fork = base_fork;
      // Grab number of bits in J and add it to the number of bits in N_max
      int chain_size_1 = bit_length(J) + 1;
      code target_1 = J + elt_N;

      // Move through all trees of the designated size
      for (Tree fork1 : trees::get_trees(db, chain_size_1)) {

        // shifts branches for the first of the nested calls.
        std::vector<int> shifted_branches{};
        for (auto block : fork1.branches) {
          shifted_branches.push_back(translate_block_std(target_1, block));
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
              //Shifts a new set of branches for the second of the nested calls ,
              shifted_branches_2.push_back(translate_block_std(target_2, block2));
              // Current tree inherits each branch except for one 
              curr_fork.branches.insert(curr_fork.branches.end(), shifted_branches_2.begin()+1, shifted_branches_2.end());

                //Saving the two possible trees to DB
                trees::insert_tree(db, curr_fork);
                curr_fork.branches.push_back(target_2);
                trees::insert_tree(db, curr_fork);

                //Reset the current fork inside the for loop
                curr_fork=base_fork;
              }
            }
          }
      }
    }
  
        /*printf("Shifted branches array:\n");
        for (auto shift : shifted_branches){
          printf("%d,", shift);
        }
        printf("\n");
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
          printf("Shifted branches array2:\n");
                  for (auto shift2 : shifted_branches_2){
                    printf("%d,", shift2);
                  }
                  printf("\n");
          // Two choices
          // // Remove the 'top' branch
          // auto ne = std::remove(shifted_branches_2.begin(), shifted_branches_2.end(), N - I_max - J); 
          // shifted_branches_2.erase(ne, shifted_branches_2.end());
          // // 2) Current tree inherits the branchs
          curr_fork.branches.insert(curr_fork.branches.end(), shifted_branches_2.begin()+1, shifted_branches_2.end());
          //save tree to db
          //printf("Saving fork to db, J= %d, target 1 = %d, target 2 = %d\n", J, target_1, target_2);
          trees::insert_tree(db, curr_fork);
          // OR
          // 1) Current Tree inherits all branches
          // curr_fork.branches.insert(curr_fork.branches.end(), shifted_branches_2.begin(), shifted_branches_2.end());
          if ((target_2 & (target_2 - 1)) != 0){
            curr_fork.branches.push_back(target_2);
            //save tree to db
           // printf("Saving fork to db, J= %d, target 1 = %d, target 2 = %d\n", J, target_1, target_2);
            trees::insert_tree(db, curr_fork);

            
          }
        }
      }
    }
  }*/
  return;
}

int main(void) {

  sqlpp::sqlite3::connection_config config;
  config.path_to_database = "trees.db";
  config.flags = SQLITE_OPEN_READWRITE;


  trees::Trees trees;
  sqlpp::sqlite3::connection db(config);
 
  for (int i  = 1; i < 5; i++){
    make_chains(db, i);
  }

  // for (int i = 0; i <= n; i++) {
  //   printf("%d: %d\n", i, phylogenees_num(i));
  // }

  return 0;
}