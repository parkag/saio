import random


def rand_bigint():
    return random.randint(1, 1E15)


def rand_boolean():
    return random.choice(['true', 'false'])


def rand_varchar():
    N = random.randint(1, 1000)
    charset = string.letters + string.digits
    return ''.join(random.choice(charset) for _ in range(N))


def rand_float8():
    return random.uniform(0, 1E10)


def rand_int4():
    return random.randint(1, 1E10)


standard_datatypes = [
    'bigint',
    'boolean',
    'varchar',
    'float8',
    'int4',
]

record_generators = {
    'bigint': rand_bigint,
    'boolean': rand_boolean,
    'varchar': rand_varchar,
    'float8': rand_float8,
    'int4': rand_int4,
}