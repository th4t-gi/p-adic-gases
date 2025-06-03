CC = clang++

all: partitions phylogenees

partitions: partitions.cpp
	$(CC) partitions.cpp -o partitions

phylogenees: phylogenees.cpp
	$(CC) phylogenees.cpp -o phylogenees

clean:
	rm -rf partitions phylogenees