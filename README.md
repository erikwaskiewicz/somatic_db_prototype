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

### Saving and loading fixtures

Fixtures are JSON files containing test data for the database, these are used when running unit tests and also can be loaded into a copy of the database when doing development work. See [Django docs](https://docs.djangoproject.com/en/4.0/howto/initial-data/) for information on fixtures.

Fixtures are stored in `analysis/fixtures`. This data will need to be updated whenever the unit tests or database models have been changed.

To load fixtures for development work, activate the conda environment and run `python manage.py loaddata <filename>`

To save a new fixture, activate the conda environment and run `python manage.py dumpdata > <filename>`. 

After updating fixtures, you may see the error shown in [issue #15](https://github.com/AWGL/somatic_db/issues/15) when running tests or loading fixtures, follow the instructions in the issue to fix this
