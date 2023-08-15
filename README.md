# Somatic variant database

### Troubleshooting

See [here](docs/common_errors.md) for common issues

### Schema
Database schemas are available for:
- the TSO500 [analysis](analysis_schema.png) database


### Setting up a local version of the database

Clone the repository, change to the directory, set up environment:

```
git clone https://github.com/AWGL/somatic_db.git
cd somatic_db
conda env create -f env.yaml
conda activate somatic_variant_db
```

Make sure that the `DB_INSTANCE` variable within `somatic_variant_db/settings.py` is set to `local` so that the app uses sqlite3 rather than postgres (postgres is used in live database):

Line 83 `somatic_variant_db/settings.py`:
```
DB_INSTANCE = 'local'
```

Set up local database:
```
python manage.py makemigrations
python manage.py migrate
```

Optional - Sometimes the models for the analysis app wont be created automatically by Django, if that happends then run this:
```
python manage.py makemigrations analysis
python manage.py migrate
```

Create the superuser, this should be called `admin` to work with upload scripts:
```
python manage.py createsuperuser
```

Load fixtures for the panels and poly list objects:
```
python manage.py loaddata panels.json
python manage.py loaddata poly_lists.json
```

Optional - Load in poly lists (`--both_checks` flag will bypass the need for two checks on each poly, for dev work only):
```
python manage.py add_poly_list --list roi/b37_polys.txt --genome 37 --both_checks
python manage.py add_poly_list --list roi/b38_polys.txt --genome 38 --both_checks
```

Optional - Load in test cases:
```
bash scripts/upload.sh analysis/test_data/Database_37/samples_dna_ws_1.csv run_1
bash scripts/upload.sh analysis/test_data/Database_37/samples_dna_ws_2.csv run_2
bash scripts/upload.sh analysis/test_data/Database_37/samples_rna_ws_1.csv run_1
bash scripts/upload.sh analysis/test_data/Database_37/samples_ctdna_ws_1.csv
bash scripts/upload.sh analysis/test_data/Database_38/samples_database_test38_DNA.csv
```

Run the database locally:
```
python manage.py runserver
```


### Setting up postgres

For running live version of the database, adapted from https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-14-04

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

To save a new fixture, activate the conda environment and run `python manage.py dumpdata <optional model name> --indent 4 > analysis/fixtures/<filename>`. e.g. `python manage.py dumpdata analysis.panel --indent 4 > analysis/fixtures/panels.json`.

To save the whole database leave the `<optional model name>` bit blank.

After updating fixtures, you may see the error shown in [issue #15](https://github.com/AWGL/somatic_db/issues/15) when running tests or loading fixtures, follow the instructions in the issue to fix this
