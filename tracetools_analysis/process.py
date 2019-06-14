#!/usr/bin/env python3
# Entrypoint/script to process events from a pickle file to build a ROS model

import argparse
import time

from tracetools_analysis.analysis import load
from tracetools_analysis.analysis import ros2_processor


def parse_args():
    parser = argparse.ArgumentParser(description='Process a pickle file generated '
                                                 'from tracing and analyze the data.')
    parser.add_argument('pickle_file',
                        help='the pickle file to import')
    return parser.parse_args()


def main():
    args = parse_args()

    pickle_filename = args.pickle_file

    start_time = time.time()
    events = load.load_pickle(pickle_filename)
    processor = ros2_processor.ros2_process(events)
    time_diff = time.time() - start_time
    print(f'processed {len(events)} events in {time_diff * 1000:.2f} ms')

    processor.get_data_model().print_model()
