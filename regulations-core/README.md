regulations-core
================
[![Build Status](https://travis-ci.org/eregs/regulations-core.svg?branch=master)](https://travis-ci.org/eregs/regulations-core)
[![Dependency Status](https://gemnasium.com/badges/github.com/eregs/regulations-core.svg)](https://gemnasium.com/github.com/eregs/regulations-core)
[![Coverage Status](https://coveralls.io/repos/github/eregs/regulations-core/badge.svg?branch=master)](https://coveralls.io/github/eregs/regulations-core?branch=master)
[![Code Climate](https://codeclimate.com/github/eregs/regulations-core/badges/gpa.svg)](https://codeclimate.com/github/eregs/regulations-core)

An API library that provides an interface for storing and retrieving regulations,
layers, etc.

This repository is part of a larger project. To read about it, please see
[http://eregs.github.io/](http://eregs.github.io/).

## Features

* Search integration with Elastic Search or Django Haystack
* Support for storage via Elastic Search or Django Models
* Separation of API into a read and a write portion
* Destruction of regulations and layers into their components, allowing
  paragraph-level access
* Schema checking for regulations

## Requirements

This library requires
* Python 2.7, 3.4, 3.5, or 3.6
* Django 1.10, or 1.11

## API Docs

[regulations-core on Read The Docs](http://regulations-core.readthedocs.org/en/latest/)

## Local development

### Tox

We use [tox](tox.readthedocs.io) to test across multiple versions of Python
and Django. To run our tests, linters, and build our docs, you'll need to
install `tox` *globally* (Tox handles virtualenvs for us).

```bash
pip install tox
# If using pyenv, consider also installing tox-pyenv
```

Then, run tests and linting across available Python versions:

```bash
tox
```

To build docs, run:

```bash
tox -e docs
```

The output will be in `docs/_build/dirhtml`.

### Running as an application

While this library is generally intended to be used within a larger project,
it can also be ran as its own application via
[Docker](https://www.docker.com/) or a local Python install. In both cases,
we'll run in `DEBUG` mode using SQLite for data storage. We don't have a turn
key solution for integrating this with search (though it can be accomplished
via a custom settings file).

To run via Docker, 
```bash
docker build . -t eregs/core  # only needed after code changes
docker run -p 8080:8080 eregs/core
```

To run via local Python, run the following inside a
[virtualenv](https://virtualenv.pypa.io/en/stable/):
```bash
pip install .
python manage.py migrate
python manage.py runserver 0.0.0.0:8080
```

In both cases, you can find the site locally at
[http://0.0.0.0:8080/](http://0.0.0.0:8080/).

## Apps included

This repository contains four Django apps, *regcore*, *regcore_read*,
*regcore_write*, and *regcore_pgsql*. The first contains shared models and
libraries. The "read" app provides read-only end-points while the "write" app
provides write-only end-points (see the next section for security
implications.) We recommend using *regcore.urls* as your url router, in which
case turning on or off read/write capabilities is as simple as including the
appropriate applications in your Django settings file. The final app,
*regcore_pgsql* contains all of the modules related to running with a
Postgres-based search index. Note that you will always need *regcore*
installed.


## Security

Note that *regcore_write* is designed to only be active inside an
organization; the assumption is that data will be pushed to public facing,
read-only (i.e. without *regcore_write*) sites separately.

When using the Elastic Search backend, data is passed as JSON, preventing
SQL-like injections. When using haystack, data is stored via Django's model
framework, which escapes SQL before it hits the db.

All data types require JSON input (which is checked.) The regulation type
has an additional schema check, which is currently not present for other
data types. Again, this liability is limited by the segmentation of read and
write end points.

As all data is assumed to be publicly visible, data is not encrypted before
it is sent to the storage engine. Data may be compressed, however.

Be sure to override the default settings for both `SECRET_KEY` and to
turn `DEBUG` off in your `local_settings.py`

## Storage-Backends

This project allows multiple backends for storing, retrieving, and searching
data. The default settings file uses Django models for data storage and
Haystack for search, but Elastic Search (1.7) or Postgres can be used instead.

### Django Models For Data, Haystack For Search

This is the default configuration. You will need to have *haystack* installed
and one of their
[backends](http://django-haystack.readthedocs.io/en/master/backend_support.html).
In your settings file, use:

```python
BACKENDS = {
    'regulations': 'regcore.db.django_models.DMRegulations',
    'layers': 'regcore.db.django_models.DMLayers',
    'notices': 'regcore.db.django_models.DMNotices',
    'diffs': 'regcore.db.django_models.DMDiffs'
}
SEARCH_HANDLER = 'regcore_read.views.haystack_search.search'
```

You will need to migrate the database (`manage.py migrate`) to get started and
rebuild the search index (`manage.py rebuild_index`) after adding documents.

### Django Models For Data, Postgres For Search

If running Django 1.10 or greater, you may skip *haystack* and rely
exclusively on Postgres for search. The current search index only indexes at
the CFR section level. Install the `psycopg` (e.g. through `pip install
regcore[backend-pgsql]`) and use the following settings:

```python
BACKENDS = {
    'regulations': 'regcore.db.django_models.DMRegulations',
    'layers': 'regcore.db.django_models.DMLayers',
    'notices': 'regcore.db.django_models.DMNotices',
    'diffs': 'regcore.db.django_models.DMDiffs'
}
SEARCH_HANDLER = 'regcore_pgsql.views.search'
APPS.append('regcore_pgsql')
```

You may wish to extend the `regcore.settings.pgsql` module for simplicity.

You will need to migrate the database (`manage.py migrate`) to get started and
rebuild the search index (`manage.py rebuild_pgsql_index`) after adding
documents.

### Elastic Search For Data and Search

If *pyelasticsearch* is installed (e.g. through `pip install
regcore[backend-elastic]`), you can use Elastic Search (1.7) for both data
storage and search. Add the following to your settings file:

```python
BACKENDS = {
    'regulations': 'regcore.db.es.ESRegulations',
    'layers': 'regcore.db.es.ESLayers',
    'notices': 'regcore.db.es.ESNotices',
    'diffs': 'regcore.db.es.ESDiffs'
}
SEARCH_HANDLER = 'regcore_read.views.es_search.search'
```

You may wish to extend the `regcore.settings.elastic` module for simplicity.


## Settings

While we provide sane default settings in `regcore/settings/base.py`, we
recommend these defaults be overridden as needed in a `local_settings.py` file.

If using Elastic Search, you will need to let the application know how to
connect to the search servers.

* `ELASTIC_SEARCH_URLS` - a list of strings which define how to connect
  to your search server(s). This is passed along to pyelasticsearch.
* `ELASTIC_SEARCH_INDEX` - the index to be used by elastic search. This
  defaults to 'eregs'

The `BACKENDS` setting (as described above) must be a dictionary of the
appropriate model names ('regulations', 'layers', etc.) to the associated
backend class. Backends can be mixed and matched, though I can't think of a
good use case for that desire.

All standard Django and haystack settings are also available; you will likely
want to override `DATABASES`, `HAYSTACK_CONNECTIONS`, `DEBUG` and certainly
`SECRET_KEY`.

##  Importing Data

### Via the `eregs` parser

The `eregs` script (see
[regulations-parser](http://github.com/eregs/regulations-parser)) includes
subcommands which will write processed data to a running API. Notably, if
`write_to` (the last step of `pipeline`) is directed at a target beginning
with `http://` or `https://`, it will write the relevant data to that host.
Note that HTTP authentication can be encoded within these urls. For example,
if the API is running on the localhost, port 8000, you could run:

```bash
$ eregs write_to http://localhost:8000/
```

See the command line
[docs](https://eregs-parser.readthedocs.io/en/latest/commandline.html) for
more detail.

### Via the `import_docs` Django command

If you've already exported data from the parser, you may import it from the
command line with the `import_docs` Django management command. It should be
given the root directory of the data as its only parameter. Note that this
does not require a running API.

```bash
$ ls /path/to/data-root
diff  layer  notice  regulation
$ python manage.py import_docs /path/to/data-root
```

### Via curl

You may also simulate sending data to a running API via curl, if you've
exported data from the parser. For example, if the API is running on the
localhost, port 8000, you could run:

```bash
$ cd /path/to/data-root
$ ls
diff  layer  notice  regulation
$ for TAIL in $(find */* -type f | sort -r) \
do \
    curl -X PUT http://localhost:8000/$TAIL -d @$TAIL \
done
```
