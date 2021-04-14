import glob

from ament_package.generate_setuptools_dict import generate_setuptools_dict
from setuptools import find_packages
from setuptools import setup

package_name = 'tracetools_analysis'
package_info = generate_setuptools_dict(
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name + '/launch', glob.glob('launch/*.launch.py')),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=['setuptools'],
    tests_require=['pytest'],
    keywords=[],
    entry_points={
        'console_scripts': [
            f'convert = {package_name}.convert:main',
            f'process = {package_name}.process:main',
            f'auto = {package_name}.scripts.auto:main',
            f'cb_durations = {package_name}.scripts.cb_durations:main',
            f'memory_usage = {package_name}.scripts.memory_usage:main',
        ],
    },
)
setup(**package_info)
