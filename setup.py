#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='issues',
    version="0.1",
    author='encorehu',
    author_email='huyoo353@126.com',
    description='a django issues',
    url='https://github.com/encorehu/django-issues',
    packages=find_packages(),
    package_dir={'issues':'issues'},
    package_data={'issues':['*.*','templates/issues/*.*']},
    zip_safe = False,
    include_package_data=True,
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
)
