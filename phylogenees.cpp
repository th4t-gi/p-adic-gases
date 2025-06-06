#include <iostream>
#include <vector>
#include <map>

int factorial(int n) {
  if (n == 0) {
    return 1;
  } else if (n == 1) {
    return 1;
  }

  return n * factorial(n-1);
}

long phylogenees_num(int n) {

  std::vector<double> previous{0.0,1.0,0.5};

  //iterate up until the number we want
  for (int i = previous.size(); i <= n; i++) {
    //calculates sum
    double sum = 0.0;
    for(int k = 2; k <= i-2; k++) {
      sum += previous[k] * previous[i-k]*(i-k);
    }

    //finds nth term
    double bn = ((i+1.0)/i)*previous[i-1] + (2.0/(i))*sum;
    
    //adds term to end of array
    previous.push_back(bn);
  }

  // calculates A000311 from b_n
  return std::ceil(factorial(n) * previous[n]);
}

struct Tree {
  std::vector<int*> branches;
  std::map<int*, int> degrees;
};

void make_chains(int label_set[], int label_set_size, Tree curr, Tree arr[]) {

  if (label_set_size == 1) return;
  else if (label_set_size == 2) {
    curr.branches.push_back(label_set);
    curr.degrees.insert({label_set, 2});
    return;
  }

  //TODO: partition label_set
  std::vector<std::vector<int[]>> partitions{};

  for (auto lambda : partitions) {
    //filter for only proper partitions
    if (lambda.size() >= 2) {
      //TODO: deep copy temp;
      Tree temp = curr;

      curr.branches.push_back(label_set);
      curr.degrees.insert({label_set, lambda.size()});

      for (auto block : lambda) {
        //size of blocks
        size_t len = sizeof(block)/sizeof(block[0]);
        //if block is a branch
        if (len >= 2) {
          make_chains(block, len, curr, arr);
        }
      }
      //TODO: save current
      curr = temp;
    }
  }

}
void _printb(unsigned int num) {
  if(!num) return;

  _printb(num>>1);
  std::cout << ((num&1) ? '1' : '0');
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


unsigned translate_block(unsigned target, unsigned x) {
  //complement of target can be understood as a list of when to shift x and when not to;
  unsigned tc = (std::bit_ceil(target) - 1) ^ target;

  //iterate over bits in tc
  while (tc) {
    //calculate least set bit in tc;
    unsigned bit = tc & -tc;
    // calculate remainder of x at current bit
    unsigned r = (bit-1) & x;
    //shift and take remainder away (equivalent to ((x - r) << 1) + r.)
    x = (x << 1) - r;
    tc -= bit;
  }

  return x;
}



int main(void) {

  unsigned int n = 5;
  // unsigned source = 7;
  unsigned target = 13;

  std::cout << "What number do you want to target?" << std::endl;
  std::cin >> target;

  unsigned source = std::pow(2, __builtin_popcount(target)) - 1;

  char res;
  std::cout << "target has size " << __builtin_popcount(target) << std::endl;
  // std::cin >> res;

  for(unsigned int i = 0; i < source; i++) {
    // translate_block(target, i);
    printf("T(%u) = %u\n", i, translate_block(target, i));
    // printf("----\n");
  }

  printf("done.\n");


  // for (int i = 0; i <= n; i++) {
  //   printf("%d: %d\n", i, phylogenees_num(i));
  // }
}