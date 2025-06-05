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


int main(void) {

  int n = 11;

  printf("n: %d\n", n);

  for (int i = 0; i <= n; i++) {
    printf("%d: %d\n", i, phylogenees_num(i));
  }
}