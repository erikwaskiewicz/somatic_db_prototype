# SVD developer guide - Unit tests

## Running unit tests

To run unit tests, activate the conda environment and run: `python manage.py test -v2`


## Saving and loading fixtures

Fixtures are JSON files containing test data for the database, these are used when running unit tests and also can be loaded into a copy of the database when doing development work. See [Django docs](https://docs.djangoproject.com/en/4.0/howto/initial-data/) for information on fixtures.

Fixtures are stored in `analysis/fixtures`. This data will need to be updated whenever the unit tests or database models have been changed.

To load fixtures for development work, activate the conda environment and run `python manage.py loaddata <filename>`

To save a new fixture, activate the conda environment and run `python manage.py dumpdata <optional model name> --indent 4 > analysis/fixtures/<filename>`. e.g. `python manage.py dumpdata analysis.panel --indent 4 > analysis/fixtures/panels.json`.

To save the whole database leave the `<optional model name>` bit blank.

After updating fixtures, you may see the error shown in [issue #15](https://github.com/AWGL/somatic_db/issues/15) when running tests or loading fixtures, follow the instructions in the issue to fix this
