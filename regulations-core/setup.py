from setuptools import find_packages, setup

setup(
    name="regcore",
    version="4.2.0",
    license="public domain",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'cached_property',
        'django>=3.1',
        'django-mptt',
        'djangorestframework',
        'jsonschema',
        'six',
        'webargs',
    ],
    extras_require={
        'backend-elastic': ['pyelasticsearch'],
        'backend-haystack': ['django-haystack'],
        'backend-pgsql': ['django>=1.10', 'psycopg2'],
    },
)
