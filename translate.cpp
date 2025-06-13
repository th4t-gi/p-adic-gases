#include <cstdint>

#include "tree.h"
#include "utils.h"
/* ######################## Translation ########################

*/

int main(void) {
  unsigned int n = 5;
  code_t source = 7;
  code_t target = 7;

  std::cout << "What number do you want to source?" << std::endl;
  std::cin >> source;

  std::cout << "What number do you want to target?" << std::endl;
  std::cin >> target;

  // unsigned source = std::pow(2, __builtin_popcount(target)) - 1;

  int sourceSize = __builtin_popcount(source);
  code_t std = (1ULL << sourceSize) - 1;
  if (sourceSize != __builtin_popcount(target)) {
    std::cout << "target and source have different size, can not translate" << std::endl;
    return 0;
  }

  printb(source, "source: ");
  printb(target, "target: ");

  for (int i = 0; i < std; i++) {
    uint64_t x = translate_block_std(source, i);

    printf("T(%llu) = %llu\n", x, translate_block(source, target, x));
  }

  Tree in{std::vector<code_t>{3}, 2};

  Tree out = in.translate(target);

  std::cout << out.to_string() << std::endl;

  printf("done.\n");
}