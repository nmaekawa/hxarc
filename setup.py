#!/usr/bin/env python

from setuptools import setup
from setuptools import find_packages
import os

import hxarc
VERSION = hxarc.__version__

requirements = [
    "Flask",
    "Flask-Bcrypt",
    "Flask-Caching",
    "Flask-DebugToolbar",
    "Flask-Login",
    "Flask-Migrate",
    "Flask-SQLAlchemy",
    "flask-webpack",
    "Flask-WTF",
    "click",
    "gunicorn",
    "itsdangerous",
    "Jinja2",
    "MarkupSafe",
    "python-dotenv",
    "pyaml",
    "SQLAlchemy",
    "Werkzeug",
    "WTForms"
]

test_requirements = [
    "pytest",
    "WebTest",
    "factory-boy",
]

setup(
    name="hxarc",
    version=VERSION,
    description="web version of https://github.com/Colin-Fredericks/hx-py/tree/master/XML_utilities",
    author="nmaekawa",
    author_email="nmaekawa@g.harvard.edu",
    url="https://github.com/nmaekawa/hxarc",
    packages=find_packages(exclude=["docs", "tests*"]),
    package_dir={'hxarc': 'hxarc'},
    include_package_data=True,
    keywords="hxpy",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Inteded audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
    install_requires=[],
    tests_requires=test_requirements,
    zip_safe=False,
)
