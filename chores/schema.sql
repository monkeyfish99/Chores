drop table if exists users;
create table users (
    id integer primary key autoincrement,
    username text not null,
    "admin" bool not null,
    hash text not null,
    root bool not null,
    assignable text not null
);

drop table if exists chores;
create table chores (
    id integer primary key autoincrement,
    chore text not null,
    enabled bool not null,
    "length" time not null,
    frequency text not null
);
   