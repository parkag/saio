load 'saio';

begin transaction;

set saio to false;
set saio to true;

set saio_seed to 0.1;
set saio_seed to 1.0;

set saio_equilibrium_factor to 1;
set saio_equilibrium_factor to 16;

set saio_initial_temperature_factor to 0.0;
set saio_initial_temperature_factor to 2.0;

set saio_temperature_reduction_factor to 0.0;
set saio_temperature_reduction_factor to 1.0;

set saio_moves_before_frozen to 1;
set saio_moves_before_frozen to 9999;
rollback;
