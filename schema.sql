DROP TABLE IF EXISTS pairs;
DROP TABLE IF EXISTS mem_cache;
DROP TABLE IF EXISTS statistics;
DROP TABLE IF EXISTS policies;

CREATE TABLE pairs (
    id serial PRIMARY KEY,
    key TEXT UNIQUE NOT NULL,
    path TEXT NOT NULL,
    size FLOAT NOT NULL,
    created_at TIMESTAMP
);

CREATE TABLE policies (
    id serial PRIMARY KEY,
    policy_name TEXT UNIQUE NOT NULL,
    description TEXT,
    policy_name_view TEXT,
    created_at TIMESTAMP,
    updaed_at TIMESTAMP
);

CREATE TABLE mem_cache (
    id serial PRIMARY KEY,
    replace_policy INTEGER,
    capacity FLOAT,
    mem_size FLOAT,
    num_of_items INTEGER,
    created_at TIMESTAMP,
    updaed_at TIMESTAMP,

    FOREIGN KEY(replace_policy) REFERENCES policies(id)
);

CREATE TABLE statistics (
    id serial PRIMARY KEY,
    requests INTEGER,
    hit FLOAT,
    miss FLOAT,
    created_at TIMESTAMP
    --> updaed_at TIMESTAMP
);

