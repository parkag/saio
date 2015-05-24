def prepare_for_saio(cur, saio_params):
    (
        eq_factor,
        initial_temp,
        temp_reduction,
        before_frozen
    ) = saio_params
    
    SQL = """
    load 'saio';
    set saio_equilibrium_factor to {eq_factor};
    set saio_initial_temperature_factor to {initial_temp};
    set saio_temperature_reduction_factor to {temp_reduction};
    set saio_moves_before_frozen to {before_frozen};
    """.format(
        eq_factor=int(eq_factor),
        initial_temp=float(initial_temp),
        temp_reduction=float(temp_reduction),
        before_frozen=int(before_frozen)
    )
    cur.execute(SQL)


def prepare_for_geqo(cur, geqo_params):
    (   
        geqo_effort,
        pool_size,
        generations,
        selection_bias
    ) = geqo_params
    SQL = """
    set geqo_effort to {geqo_effort};
    set geqo_pool_size to {pool_size};
    set geqo_generations to {generations};
    set geqo_selection_bias to {selection_bias};
    """.format(
        geqo_effort=geqo_effort,
        pool_size=pool_size,
        generations=generations,
        selection_bias=selection_bias
    )
    cur.execute(SQL)


# http://www.postgresql.org/docs/current/static/runtime-config-query.html#GUC-FROM-COLLAPSE-LIMIT
def set_collapse_limits(cur):
    SQL = ("set join_collapse_limit to 100;",
           "set from_collapse_limit to 100;")
    map(cur.execute, SQL)