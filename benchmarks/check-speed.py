#!/usr/bin/python

import json
import numpy
import os
import optparse
import psycopg2
import sys
import signal
import time

from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from sql_utils import prepare_for_geqo, prepare_for_saio, set_collapse_limits
from parameters import geqo_default_params_effort, saio_params


"""
Benchmarking script for SAIO/GEQO comparison.

It runs analyze on provided queries multiple times using SAIO or GEQO
to find out plan quality (cost), planning time and memory usage.

Usage:
python check-speed.py --query explain.sql --loops 5 --timeout 1000
"""


def main():
    parser = optparse.OptionParser()
    parser.add_option("-l", "--loops", type=int)
    parser.add_option("-t", "--timeout", type=int)
    parser.add_option("--query")
    opts, args = parser.parse_args(sys.argv)

    print "Averaging over %d loops" % opts.loops

    query = file(opts.query).read()
    #run_tests(
    #    geqo_default_params_effort, query, "query.geqo.out", 
    #    opts.loops, opts.timeout, use_saio=False
    #)
    run_tests(
        saio_params, query, "query.saio.out",
        opts.loops, opts.timeout, use_saio=True
    )


def run_tests(test_params, query, path, loops, timeout, use_saio=True):
    try:
        os.unlink(path)
    except OSError:
        pass
    for i, params in enumerate(test_params):
        print "[%d/%d]" % (i, len(test_params))
        costs, times, memory = [], [], []
        
        with psycopg2.connect(host="") as conn:
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            setup_db(conn, params, use_saio)
        
            for _ in xrange(loops):
                (
                    max_memory,
                    cost,
                    time 
                ) = run_test_case(conn, query, params, timeout, use_saio)
                memory.append(max_memory)
                costs.append(cost)
                times.append(time)
        
        output_result(
            path, params, numpy.average(costs),
            numpy.average(times), numpy.average(memory), use_saio
        )


def run_test_case(conn, query, params, timeout, use_saio):
    pid = conn.get_backend_pid()
    signal.alarm(timeout)
    try:
        cost, time = check_time(conn, query, use_saio)
    except TimeoutException:
        cost, time = -1, -1
    signal.alarm(0)
    return max_memory(pid), cost, time


def setup_db(conn, order_optimizer_parameters, use_saio):

    cur = conn.cursor()
    
    if use_saio:
        prepare_for_saio(cur, order_optimizer_parameters)
    else:
        prepare_for_geqo(cur, order_optimizer_parameters)

    set_collapse_limits(cur)


def check_time(conn, query, use_saio):

    cur = conn.cursor()

    t1 = time.time()
    cur.execute(query)
    t2 = time.time()

    analyze_result = cur.fetchone()[0]
    cost = analyze_result[0]['Plan']['Total Cost']

    execution_time = t2 - t1
    cur.close()
    return cost, float(execution_time)


def max_memory(pid):
    for line in file('/proc/%d/status' % pid):
        if not line.startswith('VmPeak'):
            continue
        num, unit = line.split()[1:3]
        return int(num)


def output_result(path, params, cost, time, memory, use_saio):
    if use_saio:
        p = "SAIO (%d, %.3f, %.3f, %d)" % params
    else:
        p = "GEQO (%d, %d, %d, %.3f)" % params
    
    print "Ran tests for %s, got %.5f %.5f %.5f" % (p, cost, time, memory)
    
    with file(path, 'a') as f:
        f.write(
            "%d\t%f\t%f\t%d\t%f\t%f\t%f\n" % (params + (cost, time, memory))
        )


class TimeoutException(Exception):
    pass


def handler(signum, frame):
    print 'ALARM'
    raise TimeoutException()


signal.signal(signal.SIGALRM, handler)


if __name__ == "__main__":
    main()
