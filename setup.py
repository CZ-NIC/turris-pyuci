import os
from setuptools import setup
from setuptools.extension import Extension

ext_compile_args = None
ext_link_args = None

if 'COVERAGE' in os.environ:
    ext_compile_args = ["-fprofile-arcs", "-ftest-coverage"]
    ext_link_args = ["-fprofile-arcs"]

setup(
    name='pyuci',
    version='0.6',
    author='CZ.NIC z.s.p.o',
    author_email='karel.koci@nic.cz',
    description='Python Uci bindings',
    long_description='Python Unified Configuration Interface bimndings.',
    license="MIT",

    packages=['euci'],
    ext_modules=[
        Extension("uci", ["ucimodule.c", "pyuci.c", "pyhelper.c"],
                  libraries=["uci"], language="c",
                  extra_compile_args=ext_compile_args,
                  extra_link_args=ext_link_args)
        ],
    )
