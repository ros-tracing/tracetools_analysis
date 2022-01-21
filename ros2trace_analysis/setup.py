from setuptools import find_packages
from setuptools import setup

package_name = 'ros2trace_analysis'

setup(
    name=package_name,
    version='3.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=['ros2cli'],
    zip_safe=True,
    maintainer=(
        'Christophe Bedard'
    ),
    maintainer_email=(
        'bedard.christophe@gmail.com'
    ),
    author='Christophe Bedard',
    author_email='christophe.bedard@apex.ai',
    url='https://gitlab.com/ros-tracing/tracetools_analysis',
    keywords=[],
    description='The trace-analysis command for ROS 2 command line tools.',
    long_description=(
        'The package provides the trace-analysis '
        'command for the ROS 2 command line tools.'
    ),
    license='Apache 2.0',
    tests_require=['pytest'],
    entry_points={
        'ros2cli.command': [
            f'trace-analysis = {package_name}.command.trace_analysis:TraceAnalysisCommand',
        ],
        'ros2cli.extension_point': [
            f'{package_name}.verb = {package_name}.verb:VerbExtension',
        ],
        f'{package_name}.verb': [
            f'convert = {package_name}.verb.convert:ConvertVerb',
            f'process = {package_name}.verb.process:ProcessVerb',
        ],
    }
)
