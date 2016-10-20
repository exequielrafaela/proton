create database testdb; grant all on testdb.* to 'root' identified by 'Temp01'; use testdb; create table customers (customer_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, first_name TEXT, last_name TEXT);
create database ggcc_prd; grant all on ggcc_prd.* to 'root' identified by 'Temp01'; use ggcc_prd; create table customers (customer_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY, first_name TEXT, last_name TEXT);

SHOW VARIABLES LIKE "%version%";
SET PASSWORD FOR 'grey_ggcc_user'@'localhost' = PASSWORD('ggcc_stg_us3r');