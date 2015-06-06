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


def test_random_query():
    ntables = random.randint(30, 35)
    
    s = RandomSchema(ntables, '')
    s.generate_tables()
    
    joins = 0
    left_joins = 0
    right_joins = 30
    
    q = RandomQuery(s, joins, left_joins, right_joins)

    setup_query = s.sql()
    query = q.explain_sql()

    print query

    run_tests(
        geqo_default_params_effort,
        setup_query,
        query,
        "random_query_r30.geqo.out", 
        LOOPS,
        TIMEOUT,
        use_saio=False
    )
    run_tests(
        saio_params,
        setup_query,
        query,
        "random_query_r30.saio.out", 
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
    test_random_query()
    #test_random_nested_query()

    

if __name__ == "__main__":
    main()

