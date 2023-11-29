# Develop
## Init
create DB
```shell
cat migrations/0_initial_postgresql.sql | psql -U postgres
```
export env variables
```shell
export $(grep -v '^#' .env | xargs)
```
create DB tables
```shell
python -m scripts.init_db_tables
```

fill db
```shell
python -m scripts.collect_raw_data
```