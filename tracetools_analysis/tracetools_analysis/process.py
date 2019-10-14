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
from typing import Optional
from typing import Tuple

from tracetools_analysis.convert import convert
from tracetools_analysis.convert import DEFAULT_CONVERT_FILE_NAME
from tracetools_analysis.loading import load_file
from tracetools_analysis.processor.ros2 import Ros2Handler
from tracetools_read.trace import is_trace_directory

from . import time_diff_to_str


def add_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'input_path',
        help='the path to a converted file to import and process, '
        'or the path to a CTF directory to convert and process')
    parser.add_argument(
        '-f', '--force-conversion', dest='force_conversion',
        action='store_true', default=False,
        help='re-convert trace directory even if converted file is found')


def parse_args():
    parser = argparse.ArgumentParser(description='Process a file converted from a trace '
                                                 'directory and output model data.')
    add_args(parser)
    return parser.parse_args()


def inspect_input_path(
    input_path: str,
    force_conversion: bool = False,
) -> Tuple[str, bool]:
    """
    Check input path for a converted file or a trace directory.

    If the input path is a file, it uses it as a converted file.
    If the input path is a directory, it checks if there is a "converted" file directly inside it,
    otherwise it tries to import the path as a trace directory.
    If `force_conversion` is set to `True`, even if a converted file is found, it will ask to
    re-create it.

    :param input_path: the path to a converted file or trace directory
    :param force_conversion: whether to re-creating converted file even if it is found
    :return:
        the path to a converted file (or `None` if could not find),
        `True` if the given converted file should be (re-)created, `False` otherwise
    """
    input_path = os.path.expanduser(input_path)
    converted_file_path = None
    # Check if not a file
    if not os.path.isfile(input_path):
        input_directory = input_path
        # Might be a (trace) directory
        # Check if there is a converted file under the given directory
        prospective_converted_file = os.path.join(input_directory, DEFAULT_CONVERT_FILE_NAME)
        if os.path.isfile(prospective_converted_file):
            # Use that as the converted input file
            converted_file_path = prospective_converted_file
            if force_conversion:
                print(f'found converted file but will re-create it: {prospective_converted_file}')
                return prospective_converted_file, True
            else:
                print(f'found converted file: {prospective_converted_file}')
                return prospective_converted_file, False
        else:
            # Check if it is a trace directory
            # Result could be unexpected because it will look for trace directories recursively
            # (e.g. '/' is a valid trace directory if there is at least one trace anywhere)
            if is_trace_directory(input_directory):
                # Convert trace directory first to create converted file
                return prospective_converted_file, True
            else:
                # We cannot do anything
                print(
                    f'cannot find either a trace directory or a converted file: {input_directory}',
                    file=sys.stderr)
                return None, None
    else:
        converted_file_path = input_path
        if force_conversion:
            # It's a file, but re-create it anyway
            print(f'found converted file but will re-create it: {converted_file_path}')
            return converted_file_path, True
        else:
            # Simplest use-case: given path is an existing converted file
            print(f'found converted file: {converted_file_path}')
            return converted_file_path, False


def process(
    input_path: str,
    force_conversion: bool = False,
) -> Optional[int]:
    """
    Process converted trace file.

    :param input_path: the path to a converted file or trace directory
    :param force_conversion: whether to re-creating converted file even if it is found
    """
    converted_file_path, create_converted_file = inspect_input_path(input_path, force_conversion)

    if converted_file_path is None:
        return 1

    # Convert trace directory to file if necessary
    if create_converted_file:
        input_directory = os.path.dirname(converted_file_path)
        input_file_name = os.path.basename(converted_file_path)
        convert(input_directory, input_file_name)

    start_time = time.time()

    events = load_file(converted_file_path)
    ros2_handler = Ros2Handler.process(events)

    time_diff = time.time() - start_time
    ros2_handler.data.print_model()
    print(f'processed {len(events)} events in {time_diff_to_str(time_diff)}')


def main():
    args = parse_args()
    input_path = args.input_path
    force_conversion = args.force_conversion

    process(input_path, force_conversion)
