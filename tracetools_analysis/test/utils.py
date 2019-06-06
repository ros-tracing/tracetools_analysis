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
