from setuptools import find_packages
from setuptools import setup

package_name = 'tracetools_analysis'

setup(
    name=package_name,
    version='0.1.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    keywords=['ROS'],
    description='Tools for analysing trace data',
    entry_points={
        'console_scripts': [
            f'convert = {package_name}.convert:main',
            f'process = {package_name}.process:main',
        ],
    },
    tests_require=['pytest'],
)
