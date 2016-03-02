"""
setup.py script for installing ccxcon package
"""
from setuptools import setup, find_packages

setup(
    name='ccxcon',
    version='0.2.0',
    license='AGPLv3',
    author='MIT ODL Engineering',
    author_email='odl-engineering@mit.edu',
    url='http://github.com/mitodl/ccxcon',
    description="CCX Connector",
    # long_description=README,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Programming Language :: Python',
    ],
    include_package_data=True,
    zip_safe=False,
)
