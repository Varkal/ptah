import json
from setuptools import setup
from path.__version import VERSION

try:
    with open('README.MD') as readme_file:
        README = readme_file.read()
except FileNotFoundError:
    README = ""

try:
    with open("Pipfile.lock") as pipfile:
        JSON_PIPFILE = json.load(pipfile)
        INSTALL_REQUIRES = []
        for key, value in dict(JSON_PIPFILE["default"]).items():
            INSTALL_REQUIRES.append("{}{}".format(key, value["version"].replace("==", "~=")))
except FileNotFoundError:
    INSTALL_REQUIRES = []

setup(
    name='ptah',
    packages=['ptah'],
    version=VERSION,
    description='',
    long_description=README,
    license='MIT',
    install_requires=INSTALL_REQUIRES,
    entry_points={
        'console_scripts': ['ptah = ptah:cli'],
    },
    data_files=[('', ['Pipfile.lock'])],
    author='Romain Moreau',
    author_email='moreau.romain83@gmail.com',
    url='https://github.com/Varkal/ptah',
    download_url='https://github.com/Varkal/ptah/archive/{}.tar.gz'.format(VERSION),
    keywords=['ptah'],
    classifiers=[
        "Programming Language :: Python :: 3"
    ],
)
