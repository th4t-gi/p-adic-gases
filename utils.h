#include <vector>
#include <iostream>

std::string binarySet(unsigned n, int width);


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

  // Tree translate(unsigned int target) {
  //   Tree translated_fork;
  //   translated_fork.setSize = setSize;
  //   // shifts branches for the first of the nested calls.
  //   for (auto block : branches) {
  //     translated_fork.branches.push_back(translate_block_std(target, block));
  //   }
  //   return translated_fork;
  // }

  void append(Tree& tree, bool exclude_top = false) {
    branches.insert(branches.end(), tree.branches.begin() + exclude_top, tree.branches.end());
  }

  std::string to_string() {
    std::string result = "[";
    bool comma = false;

    for (auto branch : branches) {
      if (comma) {
        result += ",";
      }
      comma = true;
      result += std::to_string(branch);
    }
    result += "]";
    return result;
  }

  std::string to_set_string() {
    std::string result = "[";
    bool comma = false;
    for (auto branch : branches) {
      if (comma) result += ",";
      comma = true;
      result += binarySet(branch, setSize);
    }

    return result;
  }
};

int factorial(int n);
long phylogenees_num(int n);
int bit_length(unsigned int val);

void printb(unsigned int num, const char *pre);

Tree translate_tree(unsigned int target, Tree& fork);

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
  // source compliment can be understood as a list of when to shift x to the right and when not to;
  auto sc = (std::bit_ceil(source) - 1) ^ source;

  // iterate over bits in sc
  while (sc) {
    // calculate most set bit in sc;
    auto bit = std::bit_floor(sc);

    // calculate remainder of x at current bit
    auto r = (bit - 1) & x;

    // take remainder away, shrink (>> 1), then add the remainder back. (i.e getting rid of 0s)
    x = ((x - r) >> 1) + r;
    sc -= bit;
  }

  return x;
}

constexpr uint64_t translate_block(uint64_t source, uint64_t target, uint64_t x) {
  if ((source & x) != x) {
    throw std::domain_error("input is not in source, cannot translate\n");
  }
  return translate_block_std(target, translate_block_inverse(source, x));
}