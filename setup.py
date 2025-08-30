
import setuptools
import re


def read_file(filename):
    with open(filename) as file:
        return file.read()

# version = re.search("__version__ = '([0-9.]*)'",
#                     read_file('fckprint/__init__.py')).group(1)

setuptools.setup(
    name='fckprint',
    version='1.1.2',
    author='SRSWTI Research Labs',
    author_email='team@srswti.com',
    description="imagine a world using print for debugging, and we are happy to be not be in it now.",
    long_description=read_file('README.md'),
    long_description_content_type='text/markdown',
    url='https://github.com/SRSWTI/fckprint',
    packages=setuptools.find_packages(exclude=['tests*']),
    install_requires=[
    ],
    extras_require={
        'tests': [
            'pytest',
            'pytest-cov',
        ],
        'monitoring': [
            'psutil', 
        ],
        'full': [
            'psutil',  
            'numpy',
        ],
    },
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Debuggers',
        'Topic :: Software Development :: Testing',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
    ],
    keywords='debugging monitoring performance security production tracing',
    python_requires='>=3.6',
)
