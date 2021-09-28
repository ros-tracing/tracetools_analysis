#!/usr/bin/env python3
# Copyright 2019 Robert Bosch GmbH
# Copyright 2021 Christophe Bedard
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

from tracetools_analysis.loading import load_file
from tracetools_analysis.processor import Processor
from tracetools_analysis.processor.ros2 import Ros2Handler

from . import time_diff_to_str


def add_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'input_path',
        help='the path to a converted file to import and process, '
        'or the path to a trace directory to convert and process')
    parser.add_argument(
        '-f', '--force-conversion', dest='force_conversion',
        action='store_true', default=False,
        help='re-convert trace directory even if converted file is found')
    command_group = parser.add_mutually_exclusive_group()
    command_group.add_argument(
        '-s', '--hide-results', dest='hide_results',
        action='store_true', default=False,
        help='hide/suppress results from being printed')
    command_group.add_argument(
        '-c', '--convert-only', dest='convert_only',
        action='store_true', default=False,
        help=(
            'only do the first step of converting the file, without processing it '
            '(this should not be necessary, since conversion is done automatically and is mostly '
            'just an implementation detail)'
        ))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Process ROS 2 trace data and output model data.')
    add_args(parser)
    return parser.parse_args()


def process(
    input_path: str,
    force_conversion: bool = False,
    hide_results: bool = False,
    convert_only: bool = False,
) -> int:
    """
    Process ROS 2 trace data and output model data.

    The trace data will be automatically converted into
    an internal intermediate representation if needed.

    :param input_path: the path to a converted file or trace directory
    :param force_conversion: whether to re-creating converted file even if it is found
    :param hide_results: whether to hide results and not print them
    :param convert_only: whether to only convert the file into our internal intermediate
        representation, without processing it. This should usually not be necessary since
        conversion is done automatically only when needed or when explicitly requested with
        force_conversion; conversion is mostly just an implementation detail
    """
    input_path = os.path.expanduser(input_path)
    if not os.path.exists(input_path):
        print(f'input path does not exist: {input_path}', file=sys.stderr)
        return 1

    start_time = time.time()

    events = load_file(input_path, do_convert_if_needed=True, force_conversion=force_conversion)

    # Return now if we only need to convert the file
    if convert_only:
        return 0

    processor = Processor(Ros2Handler())
    processor.process(events)

    time_diff = time.time() - start_time
    if not hide_results:
        processor.print_data()
    print(f'processed {len(events)} events in {time_diff_to_str(time_diff)}')
    return 0


def main():
    args = parse_args()

    process(
        args.input_path,
        args.force_conversion,
        args.hide_results,
        args.convert_only,
    )
