from setuptools import find_packages
from setuptools import setup

package_name = 'tracetools_analysis'

setup(
    name=package_name,
    version='0.0.1',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    maintainer='Christophe Bedard',
    maintainer_email='fixed-term.christophe.bourquebedard@de.bosch.com',
    author='Ingo Luetkebohle, Christophe Bedard',
    author_email='ingo.luetkebohle@de.bosch.com, fixed-term.christophe.bourquebedard@de.bosch.com',
    # url='',
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
