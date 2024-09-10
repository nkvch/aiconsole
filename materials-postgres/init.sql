CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    project_id TEXT NOT NULL,
    file_name TEXT NOT NULL,
    file_contents BYTEA NOT NULL,
    UNIQUE (project_id, file_name)
);