import glob

from setuptools import find_packages
from setuptools import setup

package_name = 'tracetools_analysis'

setup(
    name=package_name,
    version='0.2.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob.glob('launch/*.launch.py')),
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
    url='https://gitlab.com/micro-ROS/ros_tracing/tracetools_analysis',
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
        ],
    },
    license='Apache 2.0',
    tests_require=['pytest'],
)
