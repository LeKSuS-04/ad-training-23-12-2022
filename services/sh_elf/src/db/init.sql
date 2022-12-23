CREATE TABLE elfs (
    id SERIAL PRIMARY KEY,
    username VARCHAR(256) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL
);

CREATE TABLE santas (
    id SERIAL PRIMARY KEY,
    username VARCHAR(256) NOT NULL UNIQUE,
    password VARCHAR(256) NOT NULL
);

CREATE TABLE IF NOT EXISTS wishes (
    id VARCHAR(32) PRIMARY KEY,
    owner_id INTEGER NOT NULL,
    content VARCHAR(256) NOT NULL,
    password VARCHAR(256) NOT NULL,
    is_taken BOOLEAN NOT NULL,

    FOREIGN KEY (owner_id)
        REFERENCES elfs (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS taken_wishes (
    id VARCHAR(32) PRIMARY KEY,
    wish_id VARCHAR(32),
    santa_id INTEGER,

    FOREIGN KEY (wish_id)
        REFERENCES wishes (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE,

    FOREIGN KEY (santa_id)
        REFERENCES santas (id)
            ON DELETE CASCADE
            ON UPDATE CASCADE
);
