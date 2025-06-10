CC = clang++
INCLUDES = -lsqlite3
FLAGS = -std=c++20 -g $(INCLUDES)

EXEC = translate partitions blocks phylogenees
DEPS = utils.o api.o

.PHONY: all clean

all: $(DEPS) $(EXEC)

%.o: %.cpp
	$(CC) $(FLAGS) -c $< -o $@

# General rule for binaries
$(EXEC): %: %.cpp $(DEPS)
	$(CC) $(FLAGS) $^ -o $@

clean:
	rm -rf *.o $(EXEC)