Files overview
===============

## doc

Contains this documentation. To build it use:

    make html

in the doc directory

## scripts

Contains various snippets useful for the purpose of debugging SAIO.

## src

Contains SAIO headers and source files.
The code is well documented so there is no point in repeating the comments here.

### saio_main.c

Contains the main loop of the simulated annealing algorithm. In pseudocode:

```c
do {
    do {
        new_state = random_move()
        if (acceptable(new_state))
            state = new_state
    }
    while (!equilibrium())
    reduce_temperature()
}
while (!frozen())
return state
```

### saio.c

Defines GUC variables and manages JOIN_SEARCH_HOOK usage.


### saio_trees.c

Contains operations on tree-like structures which represent join relations between tables.


### saio_util.c

Contains functions that validate joins and generate random numbers.


### saio_recalc.c

The implementation of SAIO_recalc algorithm. The algorithm exposes such methods: 

```c
SaioAlgorithm algorithm = {
	.step = saio_recalc_step,
	.initialize = saio_recalc_initialize,
	.finalize = saio_recalc_finalize
};
```


## test

Contains regression tests for SAIO. To run tests go to the top directory 
and use:

    make installcheck

The tests will be run in alphabetical order.

For a test to pass the output generated from running an sql script from the
 `sql` subdirectory must be identical to the corresponding .out file from the
 `expected` subdirectory.


It is also possible to generate test coverage reports through gcov and lcov.
To use this you need to have your PostgreSQL installed from the source code with 
`--with-coverage` flag enabled.
    
    ./configure --with-coverage

To generate coverage reports for SAIO run:

    make installcheck
    make coverage

This will generate `coverage` directory with the coverage report. 
The test coverage should be ideally kept in the range of 95%-100%.

