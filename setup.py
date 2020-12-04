import os
from setuptools import setup
from setuptools.extension import Extension

ext_compile_args = None
ext_link_args = None

if 'COVERAGE' in os.environ:
    ext_compile_args = ["-fprofile-arcs", "-ftest-coverage"]
    ext_link_args = ["-fprofile-arcs"]


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name='pyuci',
    version='0.8.1',
    author='CZ.NIC z.s.p.o',
    author_email='karel.koci@nic.cz',
    description='Python UCI bindings',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.nic.cz/turris/pyuci",
    license="MIT",

    packages=['euci'],
    ext_modules=[
        Extension("uci", ["ucimodule.c", "pyuci.c", "pyhelper.c"],
                  libraries=["uci"], language="c",
                  extra_compile_args=ext_compile_args,
                  extra_link_args=ext_link_args)
    ],

    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
    ],
    python_requires='>=3.7',
)
