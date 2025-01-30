# Germline Classification Setup Guide

## Before You Start
Ensure you have followed the instructions in [Quick start guide](https://awgl.github.io/somatic_db/developer_guide/quick_install/) to set up the SVD application.
Ensure you have followed the instructions to [set up the SWGS module](https://awgl.github.io/somatic_db/developer_guide/swgs_quickstart/)

## Setting Up The Database
The  models for the germline classification application should have been created when setting up SVD. If they have not, or if you're adding germline classification to an existing instance, run:
```
python manage.py makemigrations germline_classification
python manage.py migrate
```
You should then load the initial setup fixtures
```
python manage.py loaddata germline_classification/fixtures/setup_fixtures.json
```
