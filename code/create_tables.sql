-- create_tables.sql
--
-- Creates idx.db to store association of cdat volume collections (.xml or .nc files) and their corresponding .idx volumes.
-- Usage: sqlite3 /path/to/idx.db < create_tables.sql

PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE datasets ( ds_id integer primary key autoincrement, pathname varchar(255));
CREATE TABLE idxfiles (idx_id integer primary key autoincrement, pathname varchar(255), ds_id integer);
COMMIT;
