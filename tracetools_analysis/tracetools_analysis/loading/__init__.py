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

"""Module for loading traces."""

import os
import pickle
import sys
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple

from tracetools_read.trace import is_trace_directory

from ..convert import convert
from ..convert import DEFAULT_CONVERT_FILE_NAME


def _inspect_input_path(
    input_path: str,
    force_conversion: bool = False,
    quiet: bool = False,
) -> Tuple[Optional[str], bool]:
    """
    Check input path for a converted file or a trace directory.

    If the input path is a file, it uses it as a converted file.
    If the input path is a directory, it checks if there is a "converted" file directly inside it,
    otherwise it tries to import the path as a trace directory.
    If `force_conversion` is set to `True`, even if a converted file is found, it will ask to
    re-create it.

    :param input_path: the path to a converted file or trace directory
    :param force_conversion: whether to re-create converted file even if it is found
    :param quiet: whether to not print any normal output
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
                if not quiet:
                    print(
                        f'found converted file but will re-create it: {prospective_converted_file}'
                    )
                return prospective_converted_file, True
            else:
                if not quiet:
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
                return None, False
    else:
        converted_file_path = input_path
        if force_conversion:
            # It's a file, but re-create it anyway
            if not quiet:
                print(f'found converted file but will re-create it: {converted_file_path}')
            return converted_file_path, True
        else:
            # Simplest use-case: given path is an existing converted file
            # No need to print anything
            return converted_file_path, False


def _convert_if_needed(
    input_path: str,
    force_conversion: bool = False,
    quiet: bool = False,
) -> Optional[str]:
    """
    Inspect input path and convert trace directory to file if necessary.

    :param input_path: the path to a converted file or trace directory
    :param force_conversion: whether to re-create converted file even if it is found
    :param quiet: whether to not print any output
    :return: the path to the converted file, or `None` if it failed
    """
    converted_file_path, create_converted_file = _inspect_input_path(
        input_path,
        force_conversion,
        quiet,
    )

    if converted_file_path is None:
        return None

    # Convert trace directory to file if necessary
    if create_converted_file:
        input_directory = os.path.dirname(converted_file_path)
        input_file_name = os.path.basename(converted_file_path)
        convert(input_directory, input_file_name)

    return converted_file_path


def load_file(
    input_path: str,
    do_convert_if_needed: bool = True,
    force_conversion: bool = False,
    quiet: bool = False,
) -> List[Dict]:
    """
    Load file containing converted trace events.

    :param input_path: the path to a converted file or trace directory
    :param do_convert_if_needed: whether to create the converted file if needed (else, let it fail)
    :param force_conversion: whether to re-create converted file even if it is found
    :param quiet: whether to not print any output
    :return: the list of events read from the file
    """
    if do_convert_if_needed or force_conversion:
        file_path = _convert_if_needed(input_path, force_conversion, quiet)
    else:
        file_path = input_path

    if file_path is None:
        raise RuntimeError(f'could not use input path: {input_path}')

    events = []
    with open(os.path.expanduser(file_path), 'rb') as f:
        p = pickle.Unpickler(f)
        while True:
            try:
                events.append(p.load())
            except EOFError:
                break  # we're done

    return events
