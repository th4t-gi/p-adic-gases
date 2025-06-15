#include <iostream>
#include <vector>
#include <cmath>

// Function to print a partition
void printPartition(const std::vector<std::vector<int>> &ans) {
  for (auto i : ans) {
    std::cout << "{ ";
    for (auto element : i) {
      std::cout << element << " ";
    }
    std::cout << "} ";
  }
  std::cout << std::endl;
}

void printPartitions(const std::vector<std::vector<std::vector<int>>> &partitions, int cap) {
  std::cout << "All partition of the set will be: " << std::endl;

  for (int i = 0; i < std::min(cap, (int) partitions.size()); i++) {
    printPartition(partitions[i]);
  }
}

// Function to generate all partitions
void Partition(const std::vector<int> &set, int index, std::vector<std::vector<int>> &curr, std::vector<std::vector<std::vector<int>>> &partitions){

  // If we have considered all elements
  // in the set print the partition
  if (index == set.size()) {
    partitions.push_back(curr);
    return;
  }

  // For each subset in the partition
  // add the current element to it
  // and recall
  for (int i = 0; i < curr.size(); i++) {
    curr[i].push_back(set[index]);
    Partition(set, index + 1, curr, partitions);
    curr[i].pop_back();
  }

  // Add the current element as a
  // singleton subset and recall
  curr.push_back({set[index]});
  Partition(set, index + 1, curr, partitions);
  curr.pop_back();
}

std::vector<int> make_list(int n) {
  std::vector<int> s(n, 0);
  for (int i = 0; i < n; i++) {
    s[i] = i + 1;
  }
  return s;
}

int bell_num_ceil(int n) {
  return std::ceil(std::pow((0.792 * n)/std::log(n+1), n));
}

int main(int argc, const char *argv[]) {
  // The size of the set

  // std::cout << "Enter the size of the set to be partitioned: ";
  // std::cin >> n;

  int n = argc ? std::stoi(argv[1]) : 4; // number of leaves


  // Initialize the set as {1, 2, ..., n}
  const std::vector<int> set = make_list(n);


  // Generate all partitions of the set
  std::vector<std::vector<std::vector<int>>> partitions;
  partitions.reserve(bell_num_ceil(n));
  
  std::vector<std::vector<int>> curr;
  Partition(set, 0, curr, partitions);
  printPartitions(partitions, 10000);

  printf("Last:");
  printPartition(partitions[partitions.size()-1]);
  printf("%lu\n", partitions.size());
  return 0;
}