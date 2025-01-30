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

## Setting Up User Groups:
- Within the admin page, click on Authentication and Authorization > Groups
- Make a new group called germline_classification
- Germline classifications performed by users from this group are counted as diagnostic - only users competent in this area and one admin account for external classification import should be added to this group

Add users to user group:
- Within the admin page, click on Authentication and Authorization > Users
- Under the Groups section, add the germline_classification group for that user and click save