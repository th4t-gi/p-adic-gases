#include <iostream>
#include <vector>

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

// Function to generate all partitions
void Partition(const std::vector<int> &set, int index, std::vector<std::vector<int>> &ans){

  // If we have considered all elements
  // in the set print the partition
  if (index == set.size()) {
    printPartition(ans);
    return;
  }

  // For each subset in the partition
  // add the current element to it
  // and recall
  for (int i = 0; i < ans.size(); i++) {
    ans[i].push_back(set[index]);
    Partition(set, index + 1, ans);
    ans[i].pop_back();
  }

  // Add the current element as a
  // singleton subset and recall
  ans.push_back({set[index]});
  Partition(set, index + 1, ans);
  ans.pop_back();
}

std::vector<int> make_list(int n) {
  std::vector<int> s(n, 0);
  for (int i = 0; i < n; i++) {
    s[i] = i + 1;
  }
  return s;
}

int main() {
  // The size of the set
  int n = 3;

  std::cout << "Enter the size of the set to be partitioned: ";
  std::cin >> n;

  std::printf("%d\n", n);

  // Initialize the set as {1, 2, ..., n}
  const std::vector<int> set = make_list(n);

  std::cout << "All partition of the set will be: " << std::endl;

  // Generate all partitions of the set
  std::vector<std::vector<int>> v;
  Partition(set, 0, v);
  printPartition(v);
  return 0;
}