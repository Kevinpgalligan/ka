from setuptools import setup
from setuptools import find_packages

setup(
    name="ka-cli",
    description="A calculator language.",
    version="1.2.0",
    url="https://github.com/Kevinpgalligan/ka",
    author="Kevin Galligan",
    author_email="galligankevinp@gmail.com",
    entry_points={
        "console_scripts": [
            "ka = ka.cli:main"
        ]
    },
    packages=find_packages("src"),
    package_dir={'': 'src'},
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
    ],
    install_requires=["PyQt5", "matplotlib", "pyreadline3"],
    python_requires=">=3.6",
)
