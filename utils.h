#include <vector>
#include <iostream>

int factorial(int n);
long phylogenees_num(int n);
int bit_length(unsigned int val);

constexpr uint64_t translate_block_std(uint64_t target, uint64_t x) {
  // complement of target can be understood as a list of when to shift x and
  // when not to;
  auto tc = (std::bit_ceil(target) - 1) ^ target;

  // iterate over bits in tc
  while (tc) {
    // calculate least set bit in tc;
    auto bit = tc & -tc;
    // calculate remainder of x at current bit
    auto r = (bit - 1) & x;
    // shift and take remainder away (equivalent to ((x - r) << 1) + r.)
    x = (x << 1) - r;
    tc -= bit;
  }

  return x;
}

constexpr uint64_t translate_block_inverse(uint64_t source, uint64_t x) {
  // source can be understood as a list of when to shift x to the right and when
  // not to;
  //  auto tc = (std::bit_ceil(target) - 1) ^ target;

  // iterate over bits in tc
  while (source) {
    // calculate least set bit in tc;
    auto bit = std::bit_floor(source);
    // calculate remainder of x at current bit
    auto r = (bit - 1) & x;
    // shift and take remainder away (equivalent to ((x - r) << 1) + r.)
    x = (x + r) >> 1;
    source -= bit;
  }

  return x;
}

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