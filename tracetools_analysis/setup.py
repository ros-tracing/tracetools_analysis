import glob

from setuptools import find_packages
from setuptools import setup

package_name = 'tracetools_analysis'

setup(
    name=package_name,
    version='3.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob.glob('launch/*.launch.py')),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=['setuptools'],
    maintainer=(
        'Christophe Bedard, '
        'Ingo Lütkebohle'
    ),
    maintainer_email=(
        'bedard.christophe@gmail.com, '
        'ingo.luetkebohle@de.bosch.com'
    ),
    author=(
        'Christophe Bedard, '
        'Ingo Lütkebohle'
    ),
    author_email=(
        'fixed-term.christophe.bourquebedard@de.bosch.com, '
        'ingo.luetkebohle@de.bosch.com'
    ),
    url='https://gitlab.com/ros-tracing/tracetools_analysis',
    keywords=[],
    description='Tools for analysing trace data.',
    long_description=(
        'This package provides tools for analysing trace data, from '
        'building a model of the trace data to providing plotting utilities.'
    ),
    entry_points={
        'console_scripts': [
            f'convert = {package_name}.convert:main',
            f'process = {package_name}.process:main',
            f'auto = {package_name}.scripts.auto:main',
            f'cb_durations = {package_name}.scripts.cb_durations:main',
            f'memory_usage = {package_name}.scripts.memory_usage:main',
        ],
    },
    license='Apache 2.0',
    tests_require=['pytest'],
)
