#pragma once
#include <vector>
#include <iostream>

typedef unsigned int code;

int factorial(int n);
long phylogenees_num(int n);
int bit_length(unsigned int val);

void printb(unsigned int num, const char *pre);

std::string binarySet(unsigned n, int width);


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