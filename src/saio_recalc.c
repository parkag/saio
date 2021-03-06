/*------------------------------------------------------------------------
 *
 * saio_main.c
 *	  setup for Simulated Annealing query optimization
 *
 * Copyright (c) 2009, PostgreSQL Global Development Group
 *
 * $PostgreSQL$
 *
 *-------------------------------------------------------------------------
 */

#include "postgres.h"

#include <math.h>

#include "utils/memutils.h"
#include "utils/hsearch.h"
#include "nodes/pg_list.h"
#include "optimizer/pathnode.h"
#include "optimizer/paths.h"

#include "saio.h"
#include "saio_util.h"
#include "saio_trees.h"

typedef struct JoinHashEntry
{
	Relids		join_relids;	/* hash key --- MUST BE FIRST */
	RelOptInfo *join_rel;
} JoinHashEntry;


static bool
list_walker(List *l, bool (*walker) (QueryTree *, bool, void *),
			bool fake, void *extra_data)
{
	ListCell	*lc;

	foreach(lc, l)
	{
		QueryTree	*tree = (QueryTree *) lfirst(lc);

		if (!walker(tree, fake, extra_data))
			return false;
	}

	return true;
}


static bool
keep_costs(QueryTree *tree, bool fake, void *extra_data)
{
	RelOptInfo		*rel = fake ? tree->tmp : tree->rel;

	tree->previous_cost = SAIO_COST(rel);
	return true;
}


static bool
remove_from_planner(QueryTree *tree, bool fake, void *extra_data)
{
	PlannerInfo *root = (PlannerInfo *) extra_data;
	RelOptInfo	*rel = fake ? tree->tmp : tree->rel;

	if (rel == NULL)
	{
		return true;
	}

	Assert(list_member_ptr(root->join_rel_list, rel));
	root->join_rel_list = list_delete_ptr(
		root->join_rel_list, rel);

	if (root->join_rel_hash != NULL) {
		if (hash_search(root->join_rel_hash, &(rel->relids),
						HASH_REMOVE, NULL) == NULL)
			elog(ERROR, "join hash table corrupted");
	}

	return true;
}


static bool
reset_memory(QueryTree *tree, bool fake, void *extra_data)
{
	MemoryContext	ctx = fake ? tree->tmpctx : tree->ctx;

	MemoryContextReset(ctx);
	return true;
}


static bool
nullify(QueryTree *tree, bool fake, void *extra_data)
{
	RelOptInfo		**rel = fake ? &tree->tmp : &tree->rel;

	*rel = NULL;
	return true;
}


static void
rebuild_join_rel_hash(PlannerInfo *root)
{
	HTAB	   *hashtab;
	HASHCTL		hash_ctl;
	ListCell   *l;

	/* Create the hash table */
	MemSet(&hash_ctl, 0, sizeof(hash_ctl));
	hash_ctl.keysize = sizeof(Relids);
	hash_ctl.entrysize = sizeof(JoinHashEntry);
	hash_ctl.hash = bitmap_hash;
	hash_ctl.match = bitmap_match;
	hash_ctl.hcxt = CurrentMemoryContext;
	hashtab = hash_create("JoinRelHashTable",
						  256L,
						  &hash_ctl,
					HASH_ELEM | HASH_FUNCTION | HASH_COMPARE | HASH_CONTEXT);

	/* Insert all the already-existing joinrels */
	foreach(l, root->join_rel_list)
	{
		RelOptInfo *rel = (RelOptInfo *) lfirst(l);
		JoinHashEntry *hentry;
		bool		found;

		hentry = (JoinHashEntry *) hash_search(hashtab,
											   &(rel->relids),
											   HASH_ENTER,
											   &found);
		Assert(!found);
		hentry->join_rel = rel;
	}

	root->join_rel_hash = hashtab;
}


static bool
switch_contexts(QueryTree *tree, bool fake, void *extra_data)
{
	MemoryContext	tmpctx;
	RelOptInfo		*tmprel;

	tmpctx = tree->tmpctx;
	tree->tmpctx = tree->ctx;
	tree->ctx = tmpctx;

	tmprel = tree->tmp;
	tree->tmp = tree->rel;
	tree->rel = tmprel;

	return true;
}


static bool
recalculate(QueryTree *tree, bool fake, void *extra_data)
{
	PlannerInfo		*root = (PlannerInfo *) extra_data;
	SaioPrivateData	*private;
	RelOptInfo		*left, *right, *rel, **tree_rel;
	MemoryContext	ctx;
	ListCell		*prev, *cur;
	bool			had_no_hash;
	int				n;

	private = (SaioPrivateData *) root->join_search_private;

	Assert(tree->left != NULL);
	Assert(tree->right != NULL);

	tree_rel = fake ? &tree->tmp : &tree->rel;

	left = tree->left->tmp == NULL ? tree->left->rel : tree->left->tmp;
	right = tree->right->tmp == NULL ? tree->right->rel : tree->right->tmp;

	if (left == NULL)
		return false;
	if (right == NULL)
		return false;

#ifdef NOT_USED
	/* if this move would create an undesirable join, don't do it */
	if (!desirable_join(root, left, right))
	{
		return false;
	}
#endif

	ctx = MemoryContextSwitchTo(fake ? tree->tmpctx : tree->ctx);
	n = list_length(root->join_rel_list);
	prev = list_tail(root->join_rel_list);
	had_no_hash = (root->join_rel_hash == NULL);
	rel = make_join_rel(root, left, right);
	MemoryContextSwitchTo(ctx);
	if (rel == NULL) {
		return false;
	}
	Assert(list_length(root->join_rel_list) == n + 1);
	/* move the list cell to the correct memory context */
	cur = list_tail(root->join_rel_list);
	root->join_rel_list = list_delete_cell(root->join_rel_list, cur, prev);
	root->join_rel_list = lappend(root->join_rel_list, rel);
	/* move the rel hash to the correct memory context */
	if (had_no_hash && root->join_rel_hash != NULL)
		rebuild_join_rel_hash(root);
	*tree_rel = rel;
	set_cheapest(rel);

	/*
	 * If this node alone has greater cost than the previous tree, we can try
	 * and eliminate it immediately.
	 */
#ifdef NOT_USED
	/*
	 * Bad idea! When recalculating known-good trees, we don't want to fail
	 * just because they're costly (or because we had bad luck with the
	 * PRNG). In any case, running compare_costs every time a tree is built
	 * makes the possibility of making an uphill move much, much lower which
	 * isn't necessarily good.
	 */
	if (!compare_costs(root, private->previous_cost,
					   SAIO_COST(rel), private->temperature))
	{
		return false;
	}
#endif
	return true;
}


static void
get_abc_paths(QueryTree *tree, QueryTree *tree1, QueryTree *tree2,
			  List **ab, List **c)
{
	List *p1, *p2;
	List *a, *b;

	p1 = get_parents(tree1, true);
	p2 = get_parents(tree2, true);

	a = list_difference_ptr(p1, p2);
	b = list_difference_ptr(p2, p1);
	*ab = list_concat(a, b);

	*c = list_difference_ptr(p1, a);

	list_free(p1);
	list_free(p2);
}


typedef struct JoinPossiblePrivate
{
	PlannerInfo	*root;
	QueryTree	*tree;
	Relids		relids2;
} JoinPossiblePrivate;


static bool
check_possible_join(QueryTree *tree, bool fake, void *extra_data)
{
	PlannerInfo		*root = (PlannerInfo *) extra_data;
	RelOptInfo	*left, *right;
	Relids		joinrelids;
	bool		ok;

	left = tree->left->tmp == NULL ? tree->left->rel : tree->left->tmp;
	right = tree->right->tmp == NULL ? tree->right->rel : tree->right->tmp;

	Assert(!bms_overlap(left->relids, right->relids));

	joinrelids = bms_union(left->relids, right->relids);
	ok = join_can_be_legal(root, left->relids, right->relids, joinrelids);

	if (!ok)
	{
		bms_free(joinrelids);
		return false;
	}

	tree->tmp = palloc(sizeof(QueryTree));
	tree->tmp->relids = joinrelids;
	return true;
}

static bool
clean_possible_join(QueryTree *tree, bool fake, void *extra_data)
{
	if (tree->tmp == NULL)
		return true;

	bms_free(tree->tmp->relids);
	pfree(tree->tmp);
	tree->tmp = NULL;
	return true;
}


static bool
joins_are_possible(PlannerInfo *root, QueryTree *tree1, QueryTree *tree2,
				   List *ab, List *c)
{
	bool				ok;


	ok = list_walker(ab, check_possible_join, true, (void *) root);

	if (!ok)
	{
		list_walker(ab, clean_possible_join, true, NULL);
		return false;
	}

	ok = list_walker(c, check_possible_join, true, (void *) root);

	list_walker(ab, clean_possible_join, true, NULL);
	list_walker(c, clean_possible_join, true, NULL);

	return ok;
}


static int
swap_and_recalc(PlannerInfo *root, QueryTree *tree,
				QueryTree *tree1, QueryTree *tree2)
{
	List		*ab, *c;
	bool		ok;
	int			move_result;

	swap_subtrees(tree1, tree2);

	get_abc_paths(tree, tree1, tree2, &ab, &c);

	/* Check if the joins make sense */
	ok = joins_are_possible(root, tree1, tree2, ab, c);
	/* ok = true; */
	if (!ok)
	{
		swap_subtrees(tree1, tree2);
		list_free(ab);
		list_free(c);
		return SAIO_MOVE_FAILED_FAST;
	}

	/* Rebuild the A and B paths */
	list_walker(ab, keep_costs, false, (void *) root);
	ok = list_walker(ab, recalculate, true, (void *) root);

	/* If that failed, reset and remove the A and B paths and return */
	if (!ok)
	{
		list_walker(ab, remove_from_planner, true, (void *) root);
		list_walker(ab, reset_memory, true, (void *) root);
		list_walker(ab, nullify, true, (void *) root);
		swap_subtrees(tree1, tree2);
		list_free(ab);
		list_free(c);
		return SAIO_MOVE_FAILED;
	}

	move_result = SAIO_MOVE_FAILED;
	/* Managed to rebuild A and B paths, now remove the C path and rebuild it */
	list_walker(c, keep_costs, false, (void *) root);
	list_walker(c, remove_from_planner, false, (void *) root);
	list_walker(c, reset_memory, false, (void *) root);
	list_walker(c, nullify, false, (void *) root);
	ok = list_walker(c, recalculate, true, (void *) root);

	/* If managed to rebuild, check for acceptability */
	if (ok)
	{
		move_result = SAIO_MOVE_DISCARDED;
		ok = acceptable(root, SAIO_COST(tree->tmp));
	}

	/* If that failed, reset and remove the A and B paths, recalculate the C
	 * path and return */
	if (!ok)
	{
		list_walker(ab, remove_from_planner, true, (void *) root);
		list_walker(ab, reset_memory, true, (void *) root);
		list_walker(ab, nullify, true, (void *) root);
		list_walker(c, remove_from_planner, true, (void *) root);
		list_walker(c, reset_memory, true, (void *) root);
		list_walker(c, nullify, true, (void *) root);

		swap_subtrees(tree1, tree2);
		ok = list_walker(c, recalculate, false, (void *) root);
		Assert(ok);
		list_free(ab);
		list_free(c);
		return move_result;
	}

	/* Everything has been rebuilt and is acceptabile */
	list_walker(ab, remove_from_planner, false, (void *) root);
	list_walker(ab, reset_memory, false, (void *) root);
	list_walker(ab, switch_contexts, false, (void *) root);
	list_walker(c, switch_contexts, false, (void *) root);
	list_walker(ab, nullify, true, (void *) root);
	list_walker(c, nullify, true, (void *) root);

	list_free(ab);
	list_free(c);
	return SAIO_MOVE_OK;
}


static saio_result
saio_recalc_step(PlannerInfo *root, QueryTree *tree, List *all_trees)
{
	List			*choices, *tmp;
	QueryTree		*tree1, *tree2;
	SaioPrivateData	*private;
	bool			ok;
	int				move_result = SAIO_MOVE_FAILED;

	if (MemoryContextIsEmpty(tree->ctx)) {
		/* rebuild the tree putting each node in its own context */
		ok = recalculate_tree_cutoff_ctx(root, tree, NULL, true);
		Assert(ok);
		if (root->join_rel_hash != NULL)
		{
			rebuild_join_rel_hash(root);
		}
	}

	private = (SaioPrivateData *) root->join_search_private;

	/* if less than four trees to choose from, return immediately */
	if (list_length(all_trees) < 4)
	{
		return SAIO_MOVE_IMPOSSIBLE;
	}

	context_enter_mem(root);

	choices = list_copy(all_trees);
	choices = list_delete_ptr(choices, llast(choices));

	tree1 = list_nth(choices, saio_randint(root, 0, list_length(choices) - 1));

	tmp = get_all_nodes(tree1);
	tmp = list_concat_unique_ptr(get_parents(tree1, false), tmp);
	tmp = list_concat_unique_ptr(get_siblings(tree1), tmp);
	choices = list_difference_ptr(choices, tmp);

	if (choices == NIL)
	{
		context_exit_mem(root);
		return SAIO_MOVE_IMPOSSIBLE;
	}

	tree2 = list_nth(choices, saio_randint(root, 0, list_length(choices) - 1));

	context_exit_mem(root);

	move_result = swap_and_recalc(root, tree, tree1, tree2);

	if (move_result != SAIO_MOVE_OK)
	{
		return move_result;
	}

	/* swap the subtrees to temporarily go back to the previous state */
	swap_subtrees(tree1, tree2);
	keep_minimum_state(root, tree, SAIO_COST(tree->rel));
	private->previous_cost = SAIO_COST(tree->rel);
	swap_subtrees(tree1, tree2);

	return SAIO_MOVE_OK;
}


static void
init_tree_contexts(QueryTree *tree)
{
	Assert(tree != NULL);

	tree->ctx = AllocSetContextCreate(CurrentMemoryContext, "SAIO node",
									  ALLOCSET_DEFAULT_MINSIZE,
									  ALLOCSET_DEFAULT_INITSIZE,
									  ALLOCSET_DEFAULT_MAXSIZE);
	tree->tmpctx = AllocSetContextCreate(CurrentMemoryContext, "SAIO tmp node",
										 ALLOCSET_DEFAULT_MINSIZE,
										 ALLOCSET_DEFAULT_INITSIZE,
										 ALLOCSET_DEFAULT_MAXSIZE);

	tree->tmp = NULL;
	if (tree->right != NULL)
		init_tree_contexts(tree->right);
	if (tree->left != NULL)
		init_tree_contexts(tree->left);
}


static void
saio_recalc_initialize(PlannerInfo *root, QueryTree *tree)
{
	SaioPrivateData	*private = (SaioPrivateData *) root->join_search_private;
	bool	ok;

	private->savelength = list_length(root->join_rel_list);
	private->savehash = root->join_rel_hash;
	/* if a hash has already been built, we need to get rid of it */
	root->join_rel_hash = NULL;

	init_tree_contexts(tree);


	ok = recalculate_tree(root, tree);
	Assert(ok);
}

static void
saio_recalc_finalize(PlannerInfo *root, QueryTree *tree)
{
	SaioPrivateData	*private = (SaioPrivateData *) root->join_search_private;

	/* restore join_rel_list and join_rel_hash */
	root->join_rel_list = list_truncate(root->join_rel_list,
										private->savelength);
	root->join_rel_hash = private->savehash;
}

SaioAlgorithm algorithm = {
	.step = saio_recalc_step,
	.initialize = saio_recalc_initialize,
	.finalize = saio_recalc_finalize
};
