#pragma once
#include <string>
#include <vector>

#include "utils.h"

class Tree {
 public:
  std::vector<code_t> branches;
  std::vector<degree_t> degrees;
  label_size_t setSize;

  Tree();
  Tree(std::vector<code_t> b, label_size_t size);
  Tree(std::vector<code_t> b, label_size_t size, std::vector<degree_t> d);
  double probability(int p);
  double term(double beta, int p, std::vector<double> interaction_arr);
  void append(Tree& tree, bool exclude_top = false);
  void addDegrees(Tree& tree);
  Tree translate(code_t target);
  std::string to_string(bool binary = false) const;
  std::string to_set_string() const;
};