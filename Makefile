CC = clang++
FLAGS = -std=c++20

all: partitions phylogenees

partitions: partitions.cpp
	$(CC) $(FLAGS) partitions.cpp -o partitions

phylogenees: phylogenees.cpp
	$(CC) $(FLAGS) phylogenees.cpp -o phylogenees

clean:
	rm -rf partitions phylogenees