#include <vector>
#include <iostream>

int factorial(int n);
long phylogenees_num(int n);
int bit_length(unsigned int val);

constexpr uint64_t translate_block_std(uint64_t target, uint64_t x);
constexpr uint64_t translate_block_inverse(uint64_t source, uint64_t x);

void printb(unsigned int num, const char *pre);

class Tree {
  public: 
    std::vector<unsigned int> branches;
    int setSize;
  // std::map<int*, int> degrees;

  Tree() {
    branches = std::vector<unsigned int>{};
    setSize = 0;
  }

  Tree(std::vector<unsigned int> b, int size) {
    branches = b;
    setSize = size;
  };

  double probability() {

    return 0;
  }
};