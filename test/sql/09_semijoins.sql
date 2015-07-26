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
    col_2 TEXT
);

LOAD 'saio';
SET saio_threshold to 2;

EXPLAIN (COSTS OFF) SELECT * FROM table_0
RIGHT JOIN table_1 ON (table_0.col_0 = table_1.col_1)
RIGHT JOIN table_2 ON (table_0.col_0 = table_2.col_1)
WHERE table_1.col_2 in (SELECT col_1 FROM table_2);

rollback;
