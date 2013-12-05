import os
import sys

from setuptools import setup, find_packages

version = '0.1'

setup(name='mezblog',
    description='blog app for blog.odonnell.nu',
    long_description='blog app for blog.odonnell.nu',
    author = "Sean O\'Donnell",
    author_email = "sean@odonnell.nu",
    url = "https://github.com/seanodonnell/mezblog",
    download_url = "https://github.com/seanodonnell/mezblog/archive/master.zip",
    keywords = ["django", "tinymce", "html", "comments", "mezzanine"],
    classifiers = [
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Environment :: Plugins",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
    ],
    version=version,
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Django >= 1.5",
        "django_html_comments",
        "django_mce_pygments",
        "django_mce_spellcheck",
        "Mezzanine",
    ],
)
