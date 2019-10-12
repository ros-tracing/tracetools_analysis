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
import time

from tracetools_analysis.conversion import ctf


def parse_args():
    parser = argparse.ArgumentParser(
        description='Convert CTF trace data to a file.')
    parser.add_argument(
        'trace_directory',
        help='the path to the main CTF trace directory')
    parser.add_argument(
        '-o', '--output-file-path', dest='output_file_path',
        help='the path to the output file to generate (default: $trace_directory/converted)')
    args = parser.parse_args()
    if args.output_file_path is None:
        args.output_file_path = os.path.join(args.trace_directory, 'converted')
    return args


def main():
    args = parse_args()

    trace_directory = args.trace_directory
    output_file_path = args.output_file_path

    print(f'importing trace directory: {trace_directory}')
    start_time = time.time()
    count = ctf.convert(trace_directory, output_file_path)
    time_diff = time.time() - start_time
    print(f'converted {count} events in {time_diff * 1000:.2f} ms')
    print(f'output written to: {output_file_path}')
