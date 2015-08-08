begin;
CREATE TABLE tenk1 (
    hundred integer,
    thousand integer
);
load 'saio';
set saio_threshold to 1;
set saio_temperature_reduction_factor to 0.99;
explain (costs off) select * from
	tenk1 t1,
	tenk1 t2
where
	t1.thousand = t2.thousand;

rollback;
