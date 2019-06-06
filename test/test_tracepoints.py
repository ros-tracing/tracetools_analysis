# Test tracetools tracepoints

import unittest
from tracetools_analysis.test.utils import *

class TestTracepoints(unittest.TestCase):

    def test_something(self):
        self.assertTrue(True)

    def test_publisher_creation(self):
        session_name = 'test-session'
        path = '/tmp'
        package_name = ''
        executable_name = ''
        run_and_trace(package_name, executable_name, session_name, path)
        event_names = get_trace_event_names(f'{path}/{session_name}')
        self.assertTrue('ros2:rcl_publisher_init' in event_names)


if __name__ == '__main__':
    unittest.main()
