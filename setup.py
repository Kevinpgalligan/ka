from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name="ka",
    description="A command-line calculator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="1.0.0",
    url="https://github.com/Kevinpgalligan/ka",
    author="Kevin Galligan",
    author_email="galligankevinp@gmail.com",
    scripts=["scripts/ka"],
    packages=find_packages("src"),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=[
        "treelib", # for visualisation
        "scipy"    # maths functions
    ]
)
