#pragma once
#include <SQLiteCpp/Database.h>

#include <json.hpp>
#include <string>
#include <vector>

#include "utils.h"

class Tree {
 public:
  std::vector<code_t> branches;
  std::vector<degree_t> degrees;
  label_size_t labelSize;
  long id;

  Tree();
  Tree(std::vector<code_t> b, label_size_t labelSize);
  Tree(std::vector<code_t> b, label_size_t labelSize, std::vector<degree_t> d);
  Tree(long id, std::vector<code_t> b, label_size_t labelSize);
  Tree(long id, std::vector<code_t> b, std::vector<degree_t> d, label_size_t labelSize);

  static Tree fromColumns(const SQLite::Column& idCol, const SQLite::Column& bCol, const SQLite::Column& dCol, label_size_t labelSize);


  double probability(int p);
  double term(double beta, int p, std::vector<double> interaction_arr);
  void append(Tree& tree, bool exclude_top = false);
  void addDegrees(Tree& tree);
  Tree translate(code_t target);
  std::string to_string(bool binary = false) const;
  std::string to_set_string() const;
};