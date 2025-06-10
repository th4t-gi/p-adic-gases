#include <iostream>
#include <map>
#include "utils.h"

struct Tree {
  std::vector<int> branches;
  // std::map<int*, int> degrees;

  Tree() {

  }

  double probability() {

    return 0;
  }
};

void make_chains(unsigned int I) {
  Tree fork;
  int I_max = std::bit_floor(I);
  fork.branches.push_back(I);

  // The case where there is only a singleton left when we combine the last
  // element and all of its buddies.
  for (int j = 1; j < I - I_max; j <<= 1) {
    // Move through all the singletons
    Tree temp = fork;
    int chain_size_0 = bit_length(I) - 2; // Size of new standard array
    for (auto fork0 : Stdchain(chain_size_0)) {
      // Shifts the branches
      std::vector<int> shifted_branches_0{};
      for (auto block : fork0.branches) {
        shifted_branches_0.push_back(translate_block_std(I - I_max - j, block));
      }

      fork.branches.insert(fork.branches.end(), shifted_branches_0.begin(), shifted_branches_0.end());
      //Save fork to db. NEED TO COMPLETE
     fork = temp;
  }
    }

  // The main case where the buddies of the last element have <|I|-1 elements
  for (int J = 0; J < (I >> 1); J++) {
    // Grab number of bits in J and add it to the number of bits in I_max
    int chain_size_1 = bit_length(J) + 1;

    // Move through all trees of the designated size
    for (auto fork1 : Stdchain(chain_size_1)) {

      // shifts branches for the first of the nested calls.
      std::vector<int> shifted_branches{};
      for (auto block : fork1.branches) {
        shifted_branches.push_back(translate_block_std(J + I_max, block));
      }
      // Current Tree inherits all branches
      fork.branches.insert(fork.branches.end(), shifted_branches.begin(), shifted_branches.end());

      // Grab size for the rest of the partition;
      int chain_size_2 = bit_length(I - I_max - J);
      // Look at other side of the partition
      for (auto fork2 : Stdchain(chain_size_2)) {
        // shifts branches for the second of the nested calls.
        std::vector<int> shifted_branches_2{};
        for (auto block2 : fork2.branches) {
          shifted_branches_2.push_back(translate_block_std(I - I_max - J, block2));
        }
        // Two choices
        // 1) Current Tree inherits all branches
        fork.branches.insert(fork.branches.end(), shifted_branches_2.begin(), shifted_branches_2.end());
        // OR
        auto ne = std::remove(shifted_branches_2.begin(), shifted_branches_2.end(), I - I_max - J); // Remove the 'top' branch
        shifted_branches_2.erase(ne, shifted_branches_2.end());
        // 2) Current tree inherits the branchs
        fork.branches.insert(fork.branches.end(), shifted_branches_2.begin(), shifted_branches_2.end());
      }
    }
  }
  return;
}

int main(void) {

  // for (int i = 0; i <= n; i++) {
  //   printf("%d: %d\n", i, phylogenees_num(i));
  // }
}