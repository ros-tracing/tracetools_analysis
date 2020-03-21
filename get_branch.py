# Copyright 2020 Christophe Bedard
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

"""Get ros2_tracing branch name from the last commit or a default value."""

import argparse
import os
import sys
from typing import List
from typing import Optional


ENV_DEFAULT_BRANCH = 'ROS2TRACING_BRANCH'
ENV_COMMIT_DESCRIPTION = 'CI_COMMIT_DESCRIPTION'
ROS2_TRACING_BRANCH_TRAILER_TOKEN = 'Ros2-tracing-branch'


def add_args(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        '-c', '--check',
        action='store_true',
        default=False,
        help='only process and print resulting branch in a verbose way',
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Extract name of the (optional) ros2_tracing branch to be used for CI',
    )
    add_args(parser)
    return parser.parse_args()


def get_trailer_value(
    trailer_name: str,
    commit_description: str,
    check: bool = False,
) -> Optional[str]:
    # Get trailer line
    trailer_lines = [
        line for line in commit_description.split('\n') if trailer_name in line
    ]
    if len(trailer_lines) == 0:
        if check:
            print(f'could not find any trailer lines for: \'{trailer_name}\'')
        return None
    elif len(trailer_lines) > 1:
        if check:
            print(
                f'found more than one trailer lines for: \'{trailer_name}\' '
                '(will use the first one)'
            )

    # Extract value
    line = trailer_lines[0]
    if not (trailer_name + ':') in line:
        if check:
            print(f'could not find: \'{trailer_name}:\'')
        return None
    key_value = line.split(':')
    if len(key_value) != 2:
        if check:
            print(f'misformed trailer line: \'{key_value}\'')
        return None
    value = key_value[1].strip()
    if len(value) == 0:
        if check:
            print(f'misformed trailer value: \'{value}\'')
        return None

    return value


def main() -> int:
    args = parse_args()
    check = args.check

    # Get default value
    default_branch = os.environ.get(ENV_DEFAULT_BRANCH, None)
    if default_branch is None:
        if check:
            print(f'could not get environment variable: \'{ENV_DEFAULT_BRANCH}\'')
        return 1

    # Get commit description
    commit_description = os.environ.get(ENV_COMMIT_DESCRIPTION, None)
    if commit_description is None:
        if check:
            print(f'could not get environment variable: \'{ENV_COMMIT_DESCRIPTION}\'')
        return None

    # Get value
    branch = get_trailer_value(
        ROS2_TRACING_BRANCH_TRAILER_TOKEN,
        commit_description,
        check,
    )

    # Print value
    prefix = 'ros2_tracing branch: ' if check else ''
    print(prefix + (branch or default_branch))

    return 0


if __name__ == '__main__':
    sys.exit(main())
