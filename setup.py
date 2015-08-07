from setuptools import setup, find_packages

setup(
    name="bk169X",
    version="0.0.1",
    author="Daniel Damiani",
    author_email="dsdamiani@gmail.com",
    description="BK Precision 169X Series control and calibration",
    long_description="A module for control and calibration of BK Precision 169X Series DC power supplies via RS-232",
    license="BSD",
    url="https://github.com/ddamiani/bk169X",
    packages=find_packages(),
    install_requires=[
        'pyserial',
        'numpy',
        'IPython',
    ],
    entry_points={
        'console_scripts': [
            'bkterm = bk169X.main:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Framework :: IPython',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Utilities',
    ],
)
