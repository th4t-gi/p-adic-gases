CC = clang++
INCLUDES_FLAGS = -lsqlite3

# Set DEBUG=1 to enable debug info, otherwise no debug info
DEBUG ?= 0

ifeq ($(DEBUG),1)
  CFLAGS = -std=c++20 -g
else
  CFLAGS = -std=c++20 -O3
endif

# Directories
SRC_DIR := src
BUILD_DIR := build

EXEC = phylogenees partitions blocks translate
DEPS = utils api tree

# Source and Object Files
OBJ_DEPS := $(addprefix $(BUILD_DIR)/, $(addsuffix .o, $(DEPS)))
EXEC_BINS := $(addprefix $(BUILD_DIR)/, $(EXEC))

# Headers
HDRS := $(wildcard $(SRC_DIR)/*.h)

TEST := test
TEST_BIN := $(BUILD_DIR)/$(TEST)

.PHONY: all clean fresh test

all: $(EXEC_BINS)

fresh:
	make clean && make all

build:
	mkdir -p $(BUILD_DIR)

$(TEST_BIN): $(SRC_DIR)/$(TEST).cpp $(OBJ_DEPS)
	$(CC) $(CFLAGS) $(INCLUDES_FLAGS) $^ -o $@

test: $(TEST_BIN)
	./$(TEST_BIN)

# Compile object files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp $(HDRS) | build
	$(CC) $(CFLAGS) -c $< -o $@

# Link executables (each one depends on its .cpp and all other .o files)
$(BUILD_DIR)/%: $(SRC_DIR)/%.cpp $(OBJ_DEPS) | build
	$(CC) $(CFLAGS) $(INCLUDES_FLAGS) $^ -o $@

clean:
	rm -rf $(BUILD_DIR)