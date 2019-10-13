#!/usr/bin/env python3
# Copyright 2019 Robert Bosch GmbH
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Entrypoint/script to process events from a converted file to build a ROS model."""

import argparse
import os
import sys
import time

from tracetools_analysis.convert import convert
from tracetools_analysis.convert import DEFAULT_CONVERT_FILE_NAME
from tracetools_analysis.loading import load_file
from tracetools_analysis.processor.ros2 import Ros2Handler
from tracetools_read.trace import is_trace_directory


def parse_args():
    parser = argparse.ArgumentParser(description='Process a file converted from a trace '
                                                 'directory and output model data.')
    parser.add_argument(
        'input_path',
        help='the path to a converted file to import and process, '
        'or the path to a CTF directory to convert and process')
    return parser.parse_args()


def main():
    args = parse_args()
    input_path = args.input_path

    start_time = time.time()

    # Check if not a file
    if not os.path.isfile(input_path):
        # Might be a trace directory
        # Check if there is a converted file
        prospective_converted_file = os.path.join(input_path, DEFAULT_CONVERT_FILE_NAME)
        if os.path.isfile(prospective_converted_file):
            # Use that as the converted input file
            print(f'found converted file: {prospective_converted_file}')
            input_path = prospective_converted_file
        else:
            # Check if it is a trace directory
            # Result could be unexpected because it will look for trace directories recursively
            if is_trace_directory(input_path):
                # Convert trace directory first to create converted file
                convert(input_path, DEFAULT_CONVERT_FILE_NAME)
                input_path = prospective_converted_file
            else:
                # We cannot do anything
                print(
                    f'cannot find either a trace directory or a converted file: {input_path}',
                    file=sys.stderr)
                return 1

    events = load_file(input_path)
    ros2_handler = Ros2Handler.process(events)

    time_diff = time.time() - start_time
    ros2_handler.data.print_model()
    print(f'processed {len(events)} events in {time_diff * 1000:.2f} ms')
