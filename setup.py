from distutils.core import setup, Extension

setup(
    name = 'PyUci',
    version = '0.1',
    description = 'Python Uci bindings',
    author = 'CZ.NIC z.s.p.o',
    author_email = 'karel.koci@nic.cz',
    long_description = 'Python Unified Configuration Interface bimndings.',
    ext_modules=[
        Extension("uci", ["ucimodule.c", "pyuci.c"], libraries=["uci"])
        ],
)
