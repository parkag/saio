#ifndef SAIO_DEBUG_H
#define SAIO_DEBUG_H

#define SAIO_TREE_FORMAT "T"

#include <printf.h>


typedef struct SaioStep {
	double			temperature;
	Cost			cost;
	int				move_result;
	int				joinrels_built;
} SaioStep;


void dump_debugging(SaioPrivateData *private);

void fprintf_relids(FILE *f, Relids relids);

void dump_query_tree(PlannerInfo *root, QueryTree *tree, QueryTree *selected1,
					 QueryTree *selected2, bool costs, char *path);

void dump_query_tree_list(PlannerInfo *root, QueryTree *tree,
						  QueryTree *selected1, QueryTree *selected2,
						  List *selected, bool costs, char *path);

void dump_query_tree_list2(PlannerInfo *root, QueryTree *tree,
						   QueryTree *selected1, QueryTree *selected2,
						   List *lselected1, List *lselected2,
						   bool costs, char *path);

void dump_costs(PlannerInfo *root, char *path);

void print_query_tree_list(char *intro, List *trees);

void trace_join(const char *path, RelOptInfo *r1, RelOptInfo *r2);

void validate_tree(QueryTree *tree);
void validate_list(List *l);

int print_tree_node(FILE *stream, const struct printf_info *info,
					const void *const *args);
int print_tree_node_arginfo(const struct printf_info *info, size_t n,
							int *argtypes, int *size);

#endif /* SAIO_DEBUG_H */
