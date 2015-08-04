GUC variables
==============

The GUC variables the module defines are:

saio
----

    default: true

A boolean that enables or disables using SAIO for planning.
If true, *all* queries with number of joins exceeding saio\_threshold will 
be planned with SAIO, if false *none*.


saio\_threshold
---------------

    range: 0 to INT_MAX
    default: 14

Determines the threshold of FROM items beyond which SAIO is used.

For smaller queries it is suitable to optimize join order
with PostgreSQL default exhaustive optimizer.


saio\_seed
---------

    range: 0.0 to 1.0
    default: 0.0

A floating point seed for the random numbers generator. If saio_seed is set 
to 0.0, the algorithm will randomize the seed with time(NULL). 
For other values, it will use the fixed seed provided.


saio\_equilibrium\_factor
-----------------------

    range: 1 to INT_MAX
    default: 16

Scaling factor for the query size, determining the number of loops before
equilibrium is reached.

Higher `equilibrium_factor` gives SAIO possibility to visit more states 
but increases the computation time.


saio\_initial\_temperature\_factor
-------------------------------

    range: 0.0 to 10.0
    default: 2.0

Factor determining the initial temperature of the system.

Higher `saio_initial_temperature_factor` gives SAIO possibility to visit more states 
but increases the computation time.

saio\_temperature\_reduction\_factor
----------------------------------

    range: 0.0 to 1.0
    default: 0.9

Factor determining how much the temperature is reduced each time equilibrium is
reached.

Lower `saio_temperature_reduction_factor` gives SAIO possibility to visit more states 
but greatly increases the computation time.


saio\_moves\_before\_frozen
------------------------

    range: 1 to INT_MAX
    default: 4

How many moves without a state change are considered a freezing condition.

