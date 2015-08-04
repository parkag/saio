The purpose of SAIO
============

The purpose of SAIO is to show how to write PostgreSQL extensions which make use
 of JOIN_SEARCH_HOOK and to stimulate the search of a better and cleaner 
non-exhaustive join order optimizer.

In the past SAIO was supposed to replace GEQO, however 
the [latest benchmarks](https://github.com/parkag/saio_benchmarks) showed that GEQO is able
 to produce better results for most of used queries.

A recognized case where SAIO generally beats GEQO is optimizing queries with
several RIGHT JOIN relations.
