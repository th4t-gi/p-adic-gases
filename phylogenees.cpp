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
  std::vector<int> branches;
  //std::map<int*, int> degrees;
};

// Function to count the number of 1s in an integers binary form
int bit_length(unsigned int val){
    int count = 0;
    while (val){
        val&= (val-1);
        count++;
    }
    return count;
}


void make_chains(int I) {
  Tree fork;
  int I_max = (std::bit_ceil(I) >> 1);
  fork.branches.push_back(I);
  
// The case where there is only a singleton left when we combine the last element and all of its buddies.
for (int j = 1; j < I - I_max; j <<=1){ //Move through all the singletons
  Tree temp = fork; 
  int chain_size_0 = bit_length(I) - 2; //Size of new standard array
  for (auto fork0 : Stdchain(chain_size_0)){

    // Shifts the branches
    std::vector<int> shifted_branches_0 {};
            for (auto block : fork0.branches){
              shifted_branches_0.push_back(translate_block(I - I_max - j, block));
            }
  
    fork.branches.insert(fork.branches.end(), shifted_branches_0.begin(), shifted_branches_0.end());
  }
  fork = temp;
}




//The main case where the buddies of the last element have <|I|-1 elements
      for (int J = 0; J < (I >> 1); J++){ 
          int chain_size_1  = bit_length(J) + 1; //Grab number of bits in J and add it to the number of bits in I_max

          for (auto fork1 : Stdchain(chain_size_1)){ //Move through all trees of the designated size
            
            //shifts branches for the first of the nested calls.
            std::vector<int> shifted_branches {};
            for (auto block : fork1.branches){
              shifted_branches.push_back(translate_block(J + I_max, block));
            }

            fork.branches.insert(fork.branches.end(), shifted_branches.begin(), shifted_branches.end()); //Current Tree inherits all branches

            int chain_size_2 = bit_length(I - I_max - J); //Grab size for the rest of the partition;
            for (auto fork2: Stdchain(chain_size_2)){ //Look at other side of the partition
                
              //shifts branches for the second of the nested calls.
                std::vector<int> shifted_branches_2 {};
                for (auto block2 : fork2.branches){
                  shifted_branches_2.push_back(translate_block(I-I_max-J, block2));
                }
                // Two choices
                fork.branches.insert(fork.branches.end(), shifted_branches_2.begin(), shifted_branches_2.end()); //Current Tree inherits all branches
                //OR 
                auto ne = std::remove(shifted_branches_2.begin(), shifted_branches_2.end(), I - I_max - J); //Remove the 'top' branch
                shifted_branches_2.erase(ne, shifted_branches_2.end());
                fork.branches.insert(fork.branches.end(),shifted_branches_2.begin(), shifted_branches_2.end()); //Current tree inherits the branchs
  
            }
          }
      }
  return;
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