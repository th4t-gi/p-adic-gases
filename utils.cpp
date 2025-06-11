#include "utils.h"

typedef unsigned int code;



/* ################### Counting functions ################
 * int factorial(n) [A000142] 1 1 2 6 24 120
 * int phylogenees_num(n) [A000311] 0 1 1 4 26 236 2752 ...
 * int bell_num(n) [A000110] 1 1 2 5 15 52 203 ...
 * fubini number [A000670] 
*/

int factorial(int n) {
  if (n == 0) {
    return 1;
  } else if (n == 1) {
    return 1;
  }

  return n * factorial(n - 1);
}

//TODO: Should we change this to the other formula?
long phylogenees_num(int n) {

  std::vector<double> previous{0.0, 1.0, 0.5};

  // iterate up until the number we want
  for (int i = previous.size(); i <= n; i++) {
    // calculates sum
    double sum = 0.0;
    for (int k = 2; k <= i - 2; k++) {
      sum += previous[k] * previous[i - k] * (i - k);
    }

    // finds nth term
    double bn = ((i + 1.0) / i) * previous[i - 1] + (2.0 / (i)) * sum;

    // adds term to end of array
    previous.push_back(bn);
  }

  // calculates A000311 from b_n
  return std::ceil(factorial(n) * previous[n]);
}

int bell_num(int n) {
  //TODO:
  return 0;
}


/* ################### Bitwise operations ################
 * 
*/

// Function to count the number of 1s in an integers binary form
int bit_length(unsigned int val) {
  int count = 0;
  while (val) {
    val &= (val - 1);
    count++;
  }
  return count;
}

/* ################### printing ################
 * 
*/

void _printb(unsigned int num) {
  if (!num)
    return;

  _printb(num >> 1);
  std::cout << ((num & 1) ? '1' : '0');
}

void printb(unsigned int num, const char *pre = "") {
  std::cout << pre;
  if (!num) {
    std::cout << '0' << std::endl;
  } else {
    _printb(num);
    std::cout << std::endl;
  }
}

std::string binarySet(unsigned n, int width) {
    std::string result = "{";
    bool comma = false;

    for (int i = 0; i < width; ++i) {
        if (n & (1 << i)) {
            if (comma) result += ",";
            result += std::to_string(i + 1);  // 1-based indexing
            comma = true;
        }
    }
    result += "}";
    return result;
}

Tree translate_tree(unsigned int target, Tree& fork) {
  Tree translated_fork;
  translated_fork.setSize = fork.setSize;
  // shifts branches for the first of the nested calls.
  for (auto block : fork.branches) {
    translated_fork.branches.push_back(translate_block_std(target, block));
  }
  return translated_fork;
}