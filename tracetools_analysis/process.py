#!/usr/bin/env python3
# Entrypoint/script to process events from a pickle file to build a ROS model

import pickle
import sys

from tracetools_analysis.analysis import ros_processor, to_pandas


def main(argv=sys.argv):
    if len(argv) != 2:
        print('usage: pickle_file')
        exit(1)

    pickle_filename = sys.argv[1]
    with open(pickle_filename, 'rb') as f:
        events = _get_events_from_pickled_file(f)
        print(f'imported {len(events)} events')
        processor = ros_processor.ros_process(events)

    df = to_pandas.callback_durations_to_df(processor)
    print(df.to_string())


def _get_events_from_pickled_file(file):
    p = pickle.Unpickler(file)
    events = []
    while True:
        try:
            events.append(p.load())
        except EOFError:
            break  # we're done
    return events
