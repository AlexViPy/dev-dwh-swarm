DROP EXTERNAL TABLE IF EXISTS src_users_adress ;
CREATE EXTERNAL TABLE src_users_adress(
    user_name TEXT,
    user_surname TEXT,
    addresses TEXT,
    city CHAR(15),
    department CHAR(15),
    local_index TEXT
)
LOCATION ('pxf://test-data/addresses.csv?PROFILE=s3:text&SERVER=default')
ON ALL FORMAT 'TEXT' (DELIMITER ',') ENCODING 'UTF8';