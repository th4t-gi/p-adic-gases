#pragma once
#include <string>
#include <vector>

#include "utils.h"

std::string binarySet(unsigned n, int width);

class Tree {
 public:
  std::vector<code> branches;
  std::vector<int> degrees;
  int setSize;

  Tree();
  Tree(std::vector<code> b, int size);
  Tree(std::vector<code> b, int size, std::vector<int> d);
  double probability(int p);
  void append(Tree& tree, bool exclude_top = false);
  void addDegrees(Tree& tree);
  Tree translate(code target);
  std::string to_string();
  std::string to_set_string();
};