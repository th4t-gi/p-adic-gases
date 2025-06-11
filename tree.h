#pragma once
#include <vector>
#include <string>
#include "util.h"

std::string binarySet(unsigned n, int width);

class Tree {
  public:
    std::vector<unsigned int> branches;
    std::vector<int> degrees;
    int setSize;

    Tree();
    Tree(std::vector<unsigned int> b, int size);
    Tree(std::vector<unsigned int> b, int size, std::vector<int> d);
    double probability();
    void append(Tree& tree, bool exclude_top = false);
    void addDegrees(Tree& tree);
    Tree translate(unsigned int target);
    std::string to_string();
    std::string to_set_string();
};