from setuptools import setup
from setuptools.extension import Extension

setup(
    name='pyuci',
    version='0.1',
    author='CZ.NIC z.s.p.o',
    author_email='karel.koci@nic.cz',
    description='Python Uci bindings',
    long_description='Python Unified Configuration Interface bimndings.',
    license="GPLv3",

    ext_modules=[
        Extension("uci", ["ucimodule.c", "pyuci.c"], libraries=["uci"])
        ],
    )
