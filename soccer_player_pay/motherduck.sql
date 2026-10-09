CREATE OR REPLACE TABLE my_db.main.all_clubs as
SELECT * from read_csv('mls_all_clubs_2014_2024.csv');
