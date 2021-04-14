from ament_package.generate_setuptools_dict import generate_setuptools_dict
from setuptools import find_packages
from setuptools import setup

package_name = 'ros2trace_analysis'
package_info = generate_setuptools_dict(
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/' + package_name, ['package.xml']),
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
    ],
    install_requires=['ros2cli'],
    tests_require=['pytest'],
    zip_safe=True,
    keywords=[],
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
setup(**package_info)
