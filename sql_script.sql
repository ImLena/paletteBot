CREATE TABLE IF NOT EXISTS usersInfo (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    chat_id VARCHAR  UNIQUE,
    clusters INTEGER
);
