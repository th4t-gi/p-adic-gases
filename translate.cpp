#include "utils.h"
#include <cstdint>
/* ######################## Translation ########################

*/

int main(void) {
  unsigned int n = 5;
  unsigned source = 7;
  unsigned target = 7;

  std::cout << "What number do you want to source?" << std::endl;
  std::cin >> source;

  std::cout << "What number do you want to target?" << std::endl;
  std::cin >> target;

  // unsigned source = std::pow(2, __builtin_popcount(target)) - 1;

  unsigned int sourceSize = __builtin_popcount(source);
  unsigned int std = (1ULL << sourceSize) - 1;
  if (sourceSize != __builtin_popcount(target)) {
    std::cout << "target and source have different size, can not translate"
              << std::endl;
    return 0;
  }

  std::vector<uint64_t> sourceArr;
  sourceArr.reserve(std);
  std::vector<uint64_t> targetArr;
  targetArr.reserve(std);
  for (int i = 0; i < std; i++) {
    // printf("source: %d, i: %d\n", source, i);
    // printf("target: %d, i: %d\n", target, i);

    sourceArr[i] = translate_block_std(source, i);
    printf("sourceArr[%d]: %d\n", i, sourceArr[i]);
    targetArr[i] = translate_block_std(target, i);
    printf("targetArr[%d]: %d\n", i, targetArr[i]);
  }

  for (int i = 0; i < std; i++) {
    // translate_block_std(target, i);
    uint64_t x = sourceArr[i];
    uint64_t y = targetArr[i];

    printf("T(%llu) = %llu\n", x, translate_block_std(target, i));
    // printf("T^-1(%llu) = %llu\n", y, translate_block_inverse(target, y));
    // printf("T(%llu) = %llu\n", translate_block_std(target, x), x);

    // printf("T^-1(T(%llu)) = %llu\n",
    //   x,
    //   translate_block_inverse(translate_block_std(target, x), x)
    // );
    // printf("T(T^-1(%llu)) = %llu\n",
    //   y,
    //   translate_block_std(translate_block_inverse(target, y), y)
    // );
  }

  printf("done.\n");
}