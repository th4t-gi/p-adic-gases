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

double phylogenees_num(int n) {

  std::vector<double> previous{0,1,0.5};

  for (int i = previous.size(); i <= n; i++) {
    double sum = 0;
    for(int k = 2; k <= n-1; k++) {
      sum += previous[k] * previous[n-k+1]*(n-k+1);
    }

    int bn = (n+2.0)/(n+1.0)*previous[n] + (2.0/(n+1))*sum;

    previous.push_back(bn);
  }

  return factorial(n) * previous[n];
}


int main(void) {

  int n = 5;

  printf("n: %d\n", n);

  for (int i = 0; i < n; i++) {
    printf("%d: %f\n", i, phylogenees_num(i));
  }
}