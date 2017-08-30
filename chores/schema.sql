drop table if exists users;
create table users (
    id integer primary key autoincrement,
    username text not null,
    "admin" bool not null,
    hash text not null,
    root bool not null
);