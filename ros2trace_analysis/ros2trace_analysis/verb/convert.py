# Copyright 2019 Apex.AI, Inc.
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

from ros2cli.verb import VerbExtension
from tracetools_analysis.convert import add_args
from tracetools_analysis.convert import convert


class ConvertVerb(VerbExtension):
    """Convert trace data to a file. DEPRECATED: use the 'process' verb directly."""

    def add_arguments(self, parser, cli_name):
        add_args(parser)

    def main(self, *, args):
        import warnings
        warnings.warn("'convert' is deprecated, use 'process' directly instead", stacklevel=2)
        return convert(
            args.trace_directory,
            args.output_file_name,
        )
