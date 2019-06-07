#!/usr/bin/env python3
# Entrypoint/script to process events from a pickle file to build a ROS model

import argparse
import pickle

from tracetools_analysis.analysis import ros_processor, to_pandas


def parse_args():
    parser = argparse.ArgumentParser(description='Process a pickle file generated from tracing and analyze the data.')
    parser.add_argument('pickle_file',
                        help='the pickle file to import')
    return parser.parse_args()


def main():
    args = parse_args()

    pickle_filename = args.pickle_file
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
