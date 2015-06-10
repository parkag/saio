import random
from check_speed import run_tests
from parameters import (
    geqo_default_params_effort,
    saio_params
)
from dynamic_schemas import star
from dynamic_schemas.query_generator import *


LOOPS = 1
TIMEOUT = 2000


def log_query(fname, query):
    with open(fname, 'w') as f:
        read_data = f.write(query)


def test_star_query(arms):
    setup_query = star.get_schema_query(arms)
    query = star.get_analyze_query2(arms)

    run_tests(
        geqo_default_params_effort, 
        setup_query,
        query,
        "star_query"+str(arms)+".geqo.out", 
        LOOPS,
        TIMEOUT,
        use_saio=False
    )
    run_tests(
        saio_params,
        setup_query,
        query,
        "star_query"+str(arms)+".saio.out",
        LOOPS,
        TIMEOUT,
        use_saio=True
    )


def test_moderate_query():
    setup_query = file('schemas/schema.sql').read()
    setup_query += file('schemas/view.sql').read()

    query = file('queries/explain.sql').read()

    run_tests(
        geqo_default_params_effort,
        setup_query,
        query,
        "moderate_query.geqo.out", 
        LOOPS,
        TIMEOUT,
        use_saio=False
    )
    run_tests(
        saio_params,
        setup_query,
        query,
        "moderate_query.saio.out", 
        LOOPS,
        TIMEOUT,
        use_saio=True
    )


def test_another_moderate_query():
    pass


def test_complex_query():
    # this is not so complex, the other one is complex
    setup_query = file('schemas/dump.sql').read()
    setup_query = None
    query = file('queries/robert.sql').read()

    run_tests(
        geqo_default_params_effort,
        setup_query,
        query,
        "complex_query.geqo.out", 
        LOOPS,
        TIMEOUT,
        use_saio=False
    )
    run_tests(
        saio_params,
        setup_query,
        query,
        "complex_query.saio.out", 
        LOOPS,
        TIMEOUT,
        use_saio=True
    )    


def test_another_complex_query():
    pass


def test_facebook_query():
    pass


def test_random_query(name, ntables, joins, left_joins, right_joins):    
    s = RandomSchema(ntables, '')
    s.generate_tables()
    q = RandomQuery(s, joins, left_joins, right_joins)

    setup_query = s.sql()
    query = q.explain_sql()

    print query
    log_query(name, setup_query+query)

    run_tests(
        geqo_default_params_effort,
        setup_query,
        query,
        name+".geqo.out", 
        LOOPS,
        TIMEOUT,
        use_saio=False
    )
    run_tests(
        saio_params,
        setup_query,
        query,
        name+".saio.out", 
        LOOPS,
        TIMEOUT,
        use_saio=True
    )

def test_random_nested_query():
    ntables = random.randint(15, 20)
    
    s = RandomSchema(ntables, '')
    s.generate_tables()
    
    joins = 6
    left_joins = 0
    right_joins = 8
    nest_level = 1
    
    q = RandomNestedQuery(s, joins, left_joins, right_joins, nest_level)

    setup_query = s.sql()
    query = q.explain_sql()

    print query

    run_tests(
        geqo_default_params_effort,
        setup_query,
        query,
        "random_nested_query3.geqo.out", 
        LOOPS,
        TIMEOUT,
        use_saio=False
    )
    run_tests(
        saio_params,
        setup_query,
        query,
        "random_nested_query3.saio.out", 
        LOOPS,
        TIMEOUT,
        use_saio=True
    )   



def main():
    #test_star_query(arms=14)
    #test_star_query(arms=25)
    #test_star_query(arms=40)
    #test_star_query(arms=80)
    #test_star_query(arms=100)
    #test_moderate_query()
    #test_complex_query()
    test_random_query('random_query_20_joins_no_constraints', 25, 20, 0, 0)
    test_random_query('random_query_20_left_joins_no_constraints', 25, 0, 20, 0)
    test_random_query('random_query_20_right_joins_no_constraints', 25, 0, 0, 20)
    test_random_query('random_query_10_joins_5_left_5_right', 25, 10, 5, 5)

    test_random_query('random_query_30_joins_no_constraints', 35, 30, 0, 0)
    test_random_query('random_query_30_left_joins_no_constraints', 35, 0, 30, 0)
    test_random_query('random_query_30_right_joins_no_constraints', 35, 0, 0, 30)
    test_random_query('random_query_10_joins_10_left_10_right', 35, 10, 10, 10)

    test_random_query('random_query_50_joins_no_constraints', 55, 50, 0, 0)
    test_random_query('random_query_50_left_joins_no_constraints', 55, 0, 50, 0)
    test_random_query('random_query_50_right_joins_no_constraints', 55, 0, 0, 50)
    test_random_query('random_query_20_joins_15_left_15_right', 55, 20, 15, 15)

    test_random_query('random_query_70_joins_no_constraints', 75, 70, 0, 0)
    test_random_query('random_query_70_left_joins_no_constraints', 75, 0, 70, 0)
    test_random_query('random_query_70_right_joins_no_constraints', 75, 0, 0, 70)
    test_random_query('random_query_30_joins_20_left_20_right', 75, 30, 20, 20)

    test_random_query('random_query_100_joins_no_constraints', 105, 100, 0, 0)
    test_random_query('random_query_100_left_joins_no_constraints', 105, 0, 100, 0)
    test_random_query('random_query_100_right_joins_no_constraints', 105, 0, 0, 100)
    test_random_query('random_query_40_joins_30_left_30_right', 105, 40, 30, 30)
    
    test_random_query('random_query_130_joins_no_constraints', 135, 130, 0, 0)
    test_random_query('random_query_130_left_joins_no_constraints', 135, 0, 130, 0)
    test_random_query('random_query_130_right_joins_no_constraints', 135, 0, 0, 130)

    #test_random_nested_query()

    

if __name__ == "__main__":
    main()

