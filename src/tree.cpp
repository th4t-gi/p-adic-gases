#include "tree.h"

#include "utils.h"

Tree::Tree() : branches{}, labelSize{0}, degrees{}, id{-1} {}
Tree::Tree(std::vector<code_t> b, label_size_t labelSize) : branches{b}, labelSize{labelSize}, degrees{}, id{-1} {}
Tree::Tree(std::vector<code_t> b, label_size_t labelSize, std::vector<degree_t> d)
    : branches{b}, labelSize{labelSize}, degrees{d}, id{-1} {}

Tree::Tree(long id, std::vector<code_t> b, label_size_t labelSize)
    : branches{b}, labelSize{labelSize}, degrees{}, id{id} {}
Tree::Tree(long id, std::vector<code_t> b, std::vector<degree_t> d, label_size_t labelSize)
    : branches{b}, labelSize{labelSize}, degrees{d}, id{id} {}

Tree Tree::fromColumns(
  const SQLite::Column& idCol, const SQLite::Column& bCol, const SQLite::Column& dCol, label_size_t labelSize
) {
  long id = idCol.getInt64();
  std::vector<code_t> b_vec = nlohmann::json::parse(bCol.getText()).get<std::vector<code_t>>();
  std::vector<degree_t> d_vec = nlohmann::json::parse(dCol.getText()).get<std::vector<degree_t>>();

  return Tree(id, b_vec, d_vec, labelSize);
}

double Tree::probability(int p) {
  double prod = 1.0;
  for (int i = 0; i < branches.size(); i++) {
    double x = falling_factorial(p, degrees[i]);
    prod *= x / (pow(p, bit_length(branches[i])) - p);
  }
  return prod;
}

// Calculates the trem of the summand for the partition equation
double Tree::term(double beta, int p, std::vector<double> interaction_arr) {
  double prod = 1.0;
  for (int i = 0; i < branches.size(); i++) {
    prod *= (falling_factorial(p, degrees[i])) /
            (pow(p, bit_length(branches[i]) + (interaction_arr[branches[i]] * beta)) - p);
  }
  return prod;
}

Tree Tree::translate(code_t target) {
  Tree translated_fork;
  translated_fork.labelSize = labelSize;
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

std::string Tree::to_string(bool binary) const {
  std::string result = "[";
  bool comma = false;
  bool hasDeg = degrees.size() > 0;

  for (int i = 0; i < branches.size(); i++) {
    auto b = branches[i];
    if (comma) result += ", ";
    comma = true;

    if (hasDeg) {
      auto d = degrees[i];
      result +=
        "\033[1m" + (binary ? std::bitset<8>(b).to_string() : std::to_string(b)) + "\033[0m:" + std::to_string(d);
    } else {
      result += (binary ? std::bitset<8>(b).to_string() : std::to_string(b));
    }
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
    result += binarySet(branch, labelSize);
  }
  result += "]";
  return result;
}