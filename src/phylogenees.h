#pragma once
#include "api.h"
#include "logger.h"
#include "tree.h"

bool check_tree(const Tree fork, code_t I_max, code_t I_min);
int make_trees(label_size_t N, APIWrapper& db, code_t IMAX, code_t IMIN);
