#!/usr/bin/env python
"""Install fakeapi package"""
from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="fakeapi",
    author="joknarf",
    author_email="joknarf@gmail.com",
    description="Fake/Mock API Rest Calls requests",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/joknarf/fakeapi",
    packages=["fakeapi"],
    scripts=[],
    use_incremental=True,
    setup_requires=['incremental'],
    install_requires=['incremental'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Utilities",
    ],
    keywords="requests API Rest api-client mock http",
    license="MIT",
)
