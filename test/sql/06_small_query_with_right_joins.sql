BEGIN;
CREATE TABLE table_0(
    col_0 TEXT,
    col_1 TEXT
);
CREATE TABLE table_1(
    col_0 TEXT,
    col_1 TEXT,
    col_2 TEXT
);
CREATE TABLE table_2(
    col_0 TEXT,
    col_1 TEXT,
    col_2 TEXT,
    col_3 TEXT
);

LOAD 'saio';
SET saio_threshold to 2;

EXPLAIN (COSTS OFF) SELECT * from table_0
RIGHT JOIN table_1 ON (table_0.col_0 = table_1.col_1)
RIGHT JOIN table_2 ON (table_0.col_0 = table_2.col_1);

rollback;
