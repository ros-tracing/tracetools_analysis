#!/usr/bin/env python3
# Entrypoint/script to setup and start an LTTng tracing session
# TODO

import sys
import time
from tracetools_analysis.tracing.lttng import *

def main(argv=sys.argv):
    if len(argv) != 3:
        print("usage: session-name /path")
        exit(1)

    session_name = argv[1]
    path = argv[2]
    # TODO fix kernel tracing
    lttng_setup(session_name, path, kernel_events=None)
    lttng_start(session_name)
    print('tracing session started')

    # TODO integrate this with launch + ROS shutdown
    time.sleep(5)

    print('stopping & destroying tracing session')
    lttng_stop(session_name)
    lttng_destroy(session_name)
