# Utils for tracetools testing

import subprocess
import babeltrace
from ..trace import *

def get_trace_event_names(trace_directory):
    """
    Get a set of event names in a trace
    :param trace_directory (str): the path to the main/top trace directory
    :return: event names (set(str))
    """
    tc = babeltrace.TraceCollection()
    tc.add_traces_recursive(trace_directory, 'ctf')

    event_names = set()

    for event in tc.events:
        event_names.add(event.name)
    
    return event_names


def run_and_trace(package_name, executable_name, session_name, path):
    """
    Setup, start tracing, and run a ROS 2 executable
    :param package_name (str): the name of the package
    :param executable_name (str): the name of the executable to run
    :param session_name (str): the name of the session
    :param directory (str): the path of the main directory to write trace data to
    """
    # Enable all events
    lttng_setup(session_name, path)
    lttng_start(session_name)
    _run(package_name, executable_name)
    lttng_stop(session_name)
    lttng_destroy(session_name)


def _run(package_name, executable_name):
    subprocess.check_call(['ros2', 'run', package_name, executable_name])
