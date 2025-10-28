-- create a separate database for your demo data
create database analytics owner airflow;

-- switch to that db (the init runner will auto-run next files against default db;
-- so place schema/table DDL in a separate file that connects explicitly)
