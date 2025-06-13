#include "utils.h"

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

double falling_factorial(int x, int k) {
  double prod = 1.0;
  for (int i = 0; i <= k - 1; i++) {
    prod *= x - i;
  }
  return prod;
}

// TODO: Should we change this to the other formula?
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
  // TODO:
  return 0;
}

/* ################### Bitwise operations ################
 *
 */

// Function to count the number of 1s in an integers binary form
int bit_length(code_t val) {
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
  if (!num) return;

  _printb(num >> 1);
  std::cout << ((num & 1) ? '1' : '0');
}

void printb(unsigned int num, const char* pre = "") {
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
/* ################### physics ################
 *
 */
std::vector<double> interaction_energy(double charges[], int size_of_charge) {
  std::vector<double> out;
  for (unsigned int J = 0; J < pow(2, size_of_charge); J++) {
    double sum1 = 0.0;
    double sum2 = 0.0;
    for (int i = 1; i <= size_of_charge; i++) {
      sum1 += (((bool)(J & (1 << (i - 1)))) * charges[i - 1]);
      sum2 += (((bool)(J & (1 << (i - 1)))) * charges[i - 1] * charges[i - 1]);
    }
    out.push_back(((sum1 * sum1) - sum2) / 2.0);
  }
  return out;
}