import numpy


# (geqo_effort, geqo_pool_size, geqo_generations, geqo_selection_bias)
geqo_params = [
    (geqo_effort, pool_size, generations, selection_bias )
    for geqo_effort in range(1, 10) # geqo_effort default 5
    for pool_size in  [0, 2, 3, 5, 10, 50] + range(100, 1000, 100)
    for generations in [0, 5, 10, 20, 40, 50, 70, 90, 100]
    for selection_bias in numpy.linspace(1.5, 2.0, 10) # geqo_selection_bias 2.0 is default
]


# (equilibrium_factor, initial_temperature, temperature_reduction_factor, steps_before_frozen)
saio_params = [
    (eq_factor, 3, temp_reduction, 2)
    for eq_factor in range(3, 12, 1)
    #for initial_temp in range(2, 5)
    for temp_reduction in numpy.linspace(0.2, 0.9, 11)
]


# (equilibrium_factor, initial_temperature, temperature_reduction_factor, steps_before_frozen)
saio_default_params = [
    (4, 2, 0.6, 2),
    (6, 2, 0.4, 2),
    (6, 2, 0.6, 2), 
    (8, 2, 0.4, 2),
    (12, 2, 0.6, 2),
    (12, 2, 0.8, 2)
]


# http://www.postgresql.org/docs/current/static/runtime-config-query.html#GUC-GEQO
geqo_default_params = [
    (5, 0, 0, 2.0)
]


# the other values will be calculated based on geqo_effort
geqo_default_params_effort = [
    (geqo_effort, 0, 0, 2.0 )
    for geqo_effort in range(1, 11)
]
