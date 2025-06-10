#include <vector>
#include <iostream>

struct Tree {
  int setSize;
  std::vector<int> branches;
  // std::map<int*, int> degrees;

  double probability();
};

int factorial(int n);
long phylogenees_num(int n);
int bit_length(unsigned int val);

constexpr uint64_t translate_block_std(uint64_t target, uint64_t x);
constexpr uint64_t translate_block_inverse(uint64_t source, uint64_t x);

void printb(unsigned int num, const char *pre);