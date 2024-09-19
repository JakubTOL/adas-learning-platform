"""
Definition of catalog that contains video materials for app scenarios. Shall contain:
- name of folder
- subpath to directory
At the end of file there is also a general directory for main folder of resources.
"""
import os


class General():
    name = 'Ogólne'
    subpath = 'General'


class Signs():
    name = 'Znaki'
    subpath = 'Signs'


class Speed():
    name = 'Prędkość'
    subpath = 'Velocity'


CATALOG_LIST = (
    General,
    Signs,
    Speed,
)

DIR_PATH = os.path.abspath(os.path.join(os.getcwd(), '..', '..', 'resources'))
