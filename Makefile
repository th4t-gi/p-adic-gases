CXX := clang++
CXXFLAGS := -std=c++20 
INCLUDES_FLAGS := -lsqlite3 -L/opt/homebrew/lib -lboost_program_options

EXEC := phylogenees #partitions blocks translate
DEPS := utils api tree

# Set DEBUG=1 to enable debug info, otherwise no debug info
DEBUG ?= 0
OPTFLAGS ?= -O2

ifeq ($(DEBUG),1)
  CXXFLAGS += -g -DDEBUG
	OPTFLAGS = -Og
	EXEC += test
endif

CXXFLAGS += $(OPTFLAGS)

# Directories
SRC_DIR := src
BUILD_DIR := build


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
	$(CXX) $(CXXFLAGS) $(INCLUDES_FLAGS) $^ -o $@

test: $(TEST_BIN)
	./$(TEST_BIN)

# Compile object files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp $(HDRS) | build
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Link executables (each one depends on its .cpp and all other .o files)
$(BUILD_DIR)/%: $(SRC_DIR)/%.cpp $(OBJ_DEPS) | build
	$(CXX) $(CXXFLAGS) $(INCLUDES_FLAGS) $^ -o $@

clean:
	rm -rf $(BUILD_DIR)