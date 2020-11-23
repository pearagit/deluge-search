
# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ''

setup(
    long_description=readme,
    name='deluge-search',
    version='0.1.0',
    python_requires='==3.*,>=3.9.0',
    author='kintsu',
    author_email='k@kintsu.io',
    entry_points={"console_scripts": ["deluge-search = deluge_search:cli"]},
    packages=['deluge_search'],
    package_dir={"": "."},
    package_data={},
    install_requires=['click==7.*,>=7.1.2', 'deluge-client==1.*,>=1.9.0', 'iterfzf==0.*,>=0.5.0', 'shell==1.*,>=1.0.1'],
    extras_require={"dev": ["black==20.*,>=20.8.0.b1", "dephell==0.*,>=0.8.3", "neovim==0.*,>=0.3.1", "neovim-remote==2.*,>=2.4.0", "pylint==2.*,>=2.6.0", "pynvim==0.*,>=0.4.2", "rope==0.*,>=0.18.0", "twine==3.*,>=3.2.0"]},
)
