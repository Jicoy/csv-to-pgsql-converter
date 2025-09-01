### how to use

`pipenv run python csv_to_pgsql.py` `[CSV-FILE]` `[TABLE-NAME]` `[SQL-OUPUT]`

### [CSV-FILE]
`test1.csv`

### [TABLE-NAME]
`users, registries`

### [SQL-OUPUT]
`output.sql <var>.sql`

### add new field with value
`python csv_to_pgsql.py spmo_data1.csv registries output.sql registry_id:start=1:end=20`


