CXX := clang++
CXXFLAGS := -std=c++20 -DSPDLOG_ACTIVE_LEVEL=SPDLOG_LEVEL_TRACE
INCLUDES_FLAGS := -lsqlite3 -lSQLiteCpp -L/opt/homebrew/lib -I/opt/homebrew/include -I/usr/local/include -L/usr/local/lib -lboost_program_options -lfmt

EXEC := phylogenees probabilities translate physics  #partitions blocks translate
DEPS := utils api tree logger

# Set DEBUG=1 to enable debug info, otherwise no debug info
DEBUG ?= 0
OPTFLAGS ?= -O2

ifeq ($(DEBUG),1)
  CXXFLAGS += -g -O0
# OPTFLAGS = -Og
	EXEC += test
else
	CXXFLAGS += $(OPTFLAGS)
endif


GIT_HASH := $(shell git rev-parse --short HEAD)
GIT_MSG  := $(shell git log -1 --pretty=%s)

LOGGER_FLAGS := $(CXXFLAGS) -I/usr/local/include -I/opt/homebrew/include -DGIT_HASH="\"$(GIT_HASH)\"" -DGIT_MSG="\"$(GIT_MSG)\""

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
$(BUILD_DIR)/logger.o: $(SRC_DIR)/logger.cpp $(HDRS) | build
	$(CXX) $(LOGGER_FLAGS) -c $< -o $@

$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp $(HDRS) | build
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Link executables (each one depends on its .cpp and all other .o files)
$(BUILD_DIR)/%: $(SRC_DIR)/%.cpp $(OBJ_DEPS) | build
	$(CXX) $(CXXFLAGS) $(INCLUDES_FLAGS) $^ -o $@

clean:
	rm -rf $(BUILD_DIR)