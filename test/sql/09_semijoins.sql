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
INSERT INTO table_0 VALUES ('a', 'b');
INSERT INTO table_0 VALUES ('c', 'd');
INSERT INTO table_1 VALUES ('a', 'a', 'a');
INSERT INTO table_1 VALUES ('b', 'b', 'b');
INSERT INTO table_1 VALUES ('c', 'c', 'c');
INSERT INTO table_1 VALUES ('d', 'd', 'd');
INSERT INTO table_2 VALUES ('a', 'b', 'c');
INSERT INTO table_2 VALUES ('b', 'c', 'd');

LOAD 'saio';
SET saio_threshold to 2;

SELECT * FROM table_0
RIGHT JOIN table_1 ON (table_0.col_0 = table_1.col_1)
RIGHT JOIN table_2 ON (table_0.col_0 = table_2.col_1)
WHERE table_2.col_1 in (SELECT col_1 FROM table_1);

ROLLBACK;

