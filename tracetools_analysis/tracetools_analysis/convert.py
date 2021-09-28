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

"""Entrypoint/script to convert CTF trace data to a file."""

import argparse
import os
import sys
import time

from tracetools_analysis.conversion import ctf

from . import time_diff_to_str


DEFAULT_CONVERT_FILE_NAME = 'converted'


def add_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        'trace_directory',
        help='the path to the main trace directory')
    parser.add_argument(
        '-o', '--output-file', dest='output_file_name', metavar='OUTPUT',
        default=DEFAULT_CONVERT_FILE_NAME,
        help='the name of the output file to generate, '
        'under $trace_directory (default: %(default)s)')


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            'Convert trace data to a file. '
            "DEPRECATED: use the 'process' verb directly."
        ),
    )
    add_args(parser)
    return parser.parse_args()


def convert(
    trace_directory: str,
    output_file_name: str = DEFAULT_CONVERT_FILE_NAME,
) -> int:
    """
    Convert trace directory to a file.

    The output file will be placed under the trace directory.

    :param trace_directory: the path to the trace directory to import
    :param outout_file_name: the name of the output file
    """
    trace_directory = os.path.expanduser(trace_directory)
    if not os.path.isdir(trace_directory):
        print(f'trace directory does not exist: {trace_directory}', file=sys.stderr)
        return 1

    print(f'converting trace directory: {trace_directory}')
    output_file_path = os.path.join(trace_directory, output_file_name)
    start_time = time.time()
    count = ctf.convert(trace_directory, output_file_path)
    time_diff = time.time() - start_time
    print(f'converted {count} events in {time_diff_to_str(time_diff)}')
    print(f'output written to: {output_file_path}')
    return 0


def main():
    args = parse_args()

    trace_directory = args.trace_directory
    output_file_name = args.output_file_name

    import warnings
    warnings.warn("'convert' is deprecated, use 'process' directly instead", stacklevel=2)
    convert(trace_directory, output_file_name)
