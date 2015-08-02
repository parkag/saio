Setup SAIO
===========

To use SAIO, you will need the PostgreSQL development headers. Compile
and install with:

    $ make
    $ sudo make install

After that log in to your PostgreSQL server with a superuser account
and issue:

    =# LOAD 'saio';
    =# SET saio_threshold TO 10;

By default all queries with the number of FROM elements exceeding saio\_threshold 
will be planned using SAIO.

To disable SAIO use:

    =# SET saio TO 'false';

Beware, if the module has been compiled against a server with assertion
checking enabled, it will run extremely slowly and it will write debugging
information to the `/tmp` directory.
