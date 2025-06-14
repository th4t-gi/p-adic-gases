#include "tree.h"

#include "utils.h"

Tree::Tree() : branches{}, setSize{0}, degrees{} {}

Tree::Tree(std::vector<code_t> b, label_size_t size) : branches{b}, setSize{size}, degrees{} {}
Tree::Tree(std::vector<code_t> b, label_size_t size, std::vector<degree_t> d) : branches{b}, setSize{size}, degrees{d} {}

double Tree::probability() { return 0; }

//Calculates the trem of the summand for the partition equation
double Tree::term(double beta, int p, std::vector<double> interaction_arr){
  double prod = 1.0;
  for (int i = 0; i< branches.size(); i++){
    prod *= (falling_factorial(p, degrees[i]))/(pow(p, bit_length(branches[i]) + (interaction_arr[branches[i]] * beta)) - p);
  }
  return prod;
}


Tree Tree::translate(code_t target) {
  Tree translated_fork;
  translated_fork.setSize = setSize;
  translated_fork.degrees = degrees;
  // shifts branches for the first of the nested calls.
  for (auto block : branches) {
    translated_fork.branches.push_back(translate_block_std(target, block));
  }
  return translated_fork;
}

void Tree::append(Tree& tree, bool exclude_top) {
  branches.insert(branches.end(), tree.branches.begin() + exclude_top, tree.branches.end());
  degrees.insert(degrees.end(), tree.degrees.begin() + exclude_top, tree.degrees.end());
}

void Tree::addDegrees(Tree& tree) {}

std::string Tree::to_string() const {
  std::string result = "[";
  bool comma = false;
  for (int i = 0; i < branches.size(); i++) {
    auto b = branches[i];
    auto d = degrees[i];
    if (comma) result += " ,";
    comma = true;
    result += "\033[1m" + std::to_string(b) + "\033[0m:" + std::to_string(d);
  }
  result += "]";

  return result;
}

std::string Tree::to_set_string() const {
  std::string result = "[";
  bool comma = false;
  for (auto branch : branches) {
    if (comma) result += ",";
    comma = true;
    result += binarySet(branch, setSize);
  }
  result += "]";
  return result;
}