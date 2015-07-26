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

SELECT table_0.* FROM table_0
RIGHT JOIN table_1 ON (table_0.col_0 = table_1.col_1)
JOIN LATERAL (
    SELECT * from table_2
    RIGHT JOIN table_1 ON table_1.col_0 = table_2.col_0
    WHERE table_0.col_0 = table_1.col_1
) AS t1 ON TRUE
LEFT JOIN LATERAL (
    SELECT * from table_2
    RIGHT JOIN table_1 ON table_1.col_0 = table_2.col_0
    LEFT JOIN (SELECT * FROM table_0) as table_3 ON TRUE
    WHERE table_0.col_0 = table_1.col_1
) AS t2 ON TRUE
LEFT JOIN LATERAL (
    SELECT * from table_2
    RIGHT JOIN table_1 ON table_1.col_0 = table_2.col_0
    LEFT JOIN (SELECT * FROM table_0) as table_3 ON TRUE
    WHERE table_0.col_0 = table_1.col_1
) AS t3 ON TRUE
RIGHT JOIN table_2 ON (table_0.col_0 = table_2.col_2);

ROLLBACK;

