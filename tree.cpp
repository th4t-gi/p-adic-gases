#include "tree.h"
#include "utils.h" // if you use binarySet

Tree::Tree() : branches{}, setSize{0}, degrees{} {}

Tree::Tree(std::vector<code> b, int size) : branches{b}, setSize{size}, degrees{} {}
Tree::Tree(std::vector<code> b, int size, std::vector<int> d)
    : branches{b}, setSize{size}, degrees{d} {}

double Tree::probability() { return 0; }

Tree Tree::translate(code target) {
  Tree translated_fork;
  translated_fork.setSize = setSize;
  translated_fork.degrees = degrees;
  // shifts branches for the first of the nested calls.
  for (auto block : branches) {
    translated_fork.branches.push_back(translate_block_std(target, block));
  }
  return translated_fork;
}

void Tree::append(Tree &tree, bool exclude_top) {
  branches.insert(branches.end(), tree.branches.begin() + exclude_top, tree.branches.end());
  degrees.insert(degrees.end(), tree.degrees.begin() + exclude_top, tree.degrees.end());
}

void Tree::addDegrees(Tree &tree) {}

std::string Tree::to_string() {
  std::string result = "[";
  bool comma = false;
  for (auto branch : branches) {
    if (comma)
      result += ",";
    comma = true;
    result += std::to_string(branch);
  }
  result += "]";
  return result;
}

std::string Tree::to_set_string() {
  std::string result = "[";
  bool comma = false;
  for (auto branch : branches) {
    if (comma)
      result += ",";
    comma = true;
    result += binarySet(branch, setSize);
  }
  result += "]";
  return result;
}