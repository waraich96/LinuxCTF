drop table if exists users;
create table users (
  id integer primary key autoincrement,
  username text not null,
  password text not null,
  solvedTasks text not null,
  totalPoints integer not null,
  prevSubmission integer not null
);
