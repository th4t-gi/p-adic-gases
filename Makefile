CC = clang++
INCLUDES_FLAGS = -lsqlite3

# Set DEBUG=1 to enable debug info, otherwise no debug info
DEBUG ?= 0

ifeq ($(DEBUG),1)
  CFLAGS = -std=c++20 -g
else
  CFLAGS = -std=c++20 -O3
endif

EXEC = translate blocks phylogenees test
DEPS = utils.o api.o tree.o

.PHONY: all clean

all: $(DEPS) $(EXEC)

fresh:
	make clean && make all

build:
	mkdir -p build

%.o: %.cpp
	$(CC) $(CFLAGS) -c $< -o $@

# General rule for binaries
$(EXEC): %: %.cpp $(DEPS) | build
	$(CC) $(CFLAGS) $(INCLUDES_FLAGS) $^ -o build/$@

clean:
	rm -rf *.o build