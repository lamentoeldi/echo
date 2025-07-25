CREATE TABLE IF NOT EXISTS users (
    id uuid primary key unique not null,
    tg_id bigint unique not null,
    tg_username varchar(32) unique default null,
    lang varchar(3) not null default 'en',
    created_at timestamp not null default now()
);