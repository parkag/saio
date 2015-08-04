SAIO [![PGXN version](https://badge.fury.io/pg/saio.svg)](https://badge.fury.io/pg/saio)[![Build Status](https://travis-ci.org/parkag/saio.svg)](https://travis-ci.org/parkag/saio)[![Coverage Status](https://coveralls.io/repos/parkag/saio/badge.svg?branch=master&service=github)](https://coveralls.io/github/parkag/saio?branch=master)
----
SAIO is a PGXN extension module for PostgreSQL that implements join order search
with Simulated Annealing.

The purpose of this module is to encourage attempts to build a non-exhaustive 
join order optimizer better than GEQO. 

Current [benchmarks](https://github.com/parkag/saio_benchmarks) show that 
currently SAIO generates worse results than GEQO - the current non-exhaustive 
join order optimizer included in PostgreSQL.

* Open source: PostgreSQL License
* Documentation: [http://saio.readthedocs.org](http://saio.readthedocs.org)

To use SAIO, you will need the PostgreSQL development headers. Compile
and install with:

    $ make
    $ sudo make install

After that log in to your PostgreSQL server with a superuser account
and issue:

    =# LOAD 'saio';
    =# SET saio\_threshold TO 10;

By default all queries with number of FROM elements exceeding saio\_threshold 
will be planned using SAIO. To disable it use:

    =# SET saio TO 'false';

Beware, if the module has been compiled against a server with assertion
checking enabled, it will run extremely slowly and it will write debugging
information to the `/tmp` directory.

