CC = clang++
INCLUDES_FLAGS = -lsqlite3
FLAGS = -std=c++20 -g

EXEC = translate blocks phylogenees
DEPS = utils.o api.o tree.o

.PHONY: all clean

all: $(DEPS) $(EXEC)

fresh:
	make clean && make all

%.o: %.cpp
	$(CC) $(FLAGS) -c $< -o $@

# General rule for binaries
$(EXEC): %: %.cpp $(DEPS)
	$(CC) $(FLAGS) $(INCLUDES_FLAGS) $^ -o $@

clean:
	rm -rf *.o $(EXEC)