PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE datasets ( ds_id INTEGER PRIMARY KEY AUTOINCREMENT, name varchar(255), last_access default current_timestamp);
CREATE TABLE idxfiles (idx_id integer primary key autoincrement, idx_path varchar(255));
CREATE TABLE ncfiles (nc_id integer primary key autoincrement, nc_path varchar(255));
CREATE TABLE vars (var_id integer primary key autoincrement, ds_id integer, varname varchar(32), idx_id integer);
CREATE TABLE timesteps (id integer primary key autoincrement, var_id integer, timestep integer, nc_id integer, converted integer default 0);
COMMIT;
