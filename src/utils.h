#pragma once
#include <iostream>
#include <vector>

typedef uint16_t code_t;
typedef uint8_t label_size_t;
typedef uint8_t degree_t;

int factorial(int n);
double falling_factorial(int n, int k);
long phylogenees_num(int n);
int bit_length(code_t val);

std::vector<double> interaction_energy(double charges[], int size_of_charge);

void printb(unsigned int num, const char* pre);

std::string binarySet(unsigned n, int width);

template <typename T>
T question(std::string str, T def) {
  T input = def;
  std::cout << str;
  if (!(std::cin >> input)) {
    // If input fails (e.g., user presses Enter or types invalid value)
    std::cin.clear();
    std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
    return def;
  }
  return input;
}

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
  // source compliment can be understood as a list of when to shift x to the
  // right and when not to;
  auto sc = (std::bit_ceil(source) - 1) ^ source;

  // iterate over bits in sc
  while (sc) {
    // calculate most set bit in sc;
    auto bit = std::bit_floor(sc);

    // calculate remainder of x at current bit
    auto r = (bit - 1) & x;

    // take remainder away, shrink (>> 1), then add the remainder back. (i.e
    // getting rid of 0s)
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