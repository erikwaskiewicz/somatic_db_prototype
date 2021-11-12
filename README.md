# Somatic variant database

### Setting up postgres

https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04

```
CREATE DATABASE somatic_variant_db;
CREATE USER somatic_variant_db_user WITH PASSWORD 'password';

ALTER ROLE somatic_variant_db_user SET client_encoding TO 'utf8';
ALTER ROLE somatic_variant_db_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE somatic_variant_db_user SET timezone TO 'Europe/London';

GRANT ALL PRIVILEGES ON DATABASE somatic_variant_db TO somatic_variant_db_user;
```



### Running unit tests

To run unit tests, activate the conda environment and run: `python manage.py test -v2`
