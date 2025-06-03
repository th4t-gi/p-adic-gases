#include <iostream>
#include <vector>

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


int main(void) {

  int n = 11;

  printf("n: %d\n", n);

  for (int i = 0; i <= n; i++) {
    printf("%d: %\n", i, phylogenees_num(i));
  }
}