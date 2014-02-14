from setuptools import setup, find_packages

setup(
    # Metadata
    name="braijsa",
    version="0.0.1",
    description="Admin dashboard for Datomic",
    url="https://bitbucket.org/locusdevelopment/bottom",
    author="InVitae Inc.",
    author_email="developers@invitae.com",
    maintainer="Chris Allen",
    maintainer_email="chris.allen@invitae.com",
    license="MIT",
    install_requires=[
        "iPython",
        "nose",
        "PyHamcrest",
        "edn_format",
        "mock",
        "requests",
        "coverage"],
    # Packaging Instructions
    packages=find_packages())
