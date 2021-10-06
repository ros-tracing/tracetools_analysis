# tracetools_analysis

[![pipeline status](https://gitlab.com/ros-tracing/tracetools_analysis/badges/master/pipeline.svg)](https://gitlab.com/ros-tracing/tracetools_analysis/commits/master)
[![codecov](https://codecov.io/gl/ros-tracing/tracetools_analysis/branch/master/graph/badge.svg)](https://codecov.io/gl/ros-tracing/tracetools_analysis)

Analysis tools for [ROS 2 tracing](https://gitlab.com/ros-tracing/ros2_tracing).

## Trace analysis

After generating a trace (see [`ros2_tracing`](https://gitlab.com/ros-tracing/ros2_tracing#tracing)), we can analyze it to extract useful execution data.

### Commands

Then we can process a trace to create a data model which could be queried for analysis.

```
$ ros2 trace-analysis process /path/to/trace/directory
```

Note that this simply outputs lightly-processed ROS 2 trace data which is split into a number of pandas `DataFrame`s.
This can be used to quickly check the trace data.
For real data processing/trace analysis, see [*Analysis*](#analysis).

Since CTF traces (the output format of the [LTTng](https://lttng.org/) tracer) are very slow to read, the trace is first converted into a single file which can be read much faster and can be re-used to run many analyses.
This is done automatically, but if the trace changed after the file was generated, it can be re-generated using the `--force-conversion` option.
Run with `--help` to see all options.

### Analysis

The command above will process and output raw data models.
We need to actually analyze the data and display some results.
We recommend doing this in a Jupyter Notebook, but you can do this in a normal Python file.

```shell
$ jupyter notebook
```

Navigate to the [`analysis/`](./tracetools_analysis/analysis/) directory, and select one of the provided notebooks, or create your own!

For example:

```python
from tracetools_analysis.loading import load_file
from tracetools_analysis.processor import Processor
from tracetools_analysis.processor.cpu_time import CpuTimeHandler
from tracetools_analysis.processor.ros2 import Ros2Handler
from tracetools_analysis.utils.cpu_time import CpuTimeDataModelUtil
from tracetools_analysis.utils.ros2 import Ros2DataModelUtil

# Load trace directory or converted trace file
events = load_file('/path/to/trace/or/converted/file')

# Process
ros2_handler = Ros2Handler()
cpu_handler = CpuTimeHandler()

Processor(ros2_handler, cpu_handler).process(events)

# Use data model utils to extract information
ros2_util = Ros2DataModelUtil(ros2_handler.data)
cpu_util = CpuTimeDataModelUtil(cpu_handler.data)

callback_symbols = ros2_util.get_callback_symbols()
callback_object, callback_symbol = list(callback_symbols.items())[0]
callback_durations = ros2_util.get_callback_durations(callback_object)
time_per_thread = cpu_util.get_time_per_thread()
# ...

# Display, e.g., with bokeh, matplotlib, print, etc.
print(callback_symbol)
print(callback_durations)

print(time_per_thread)
# ...
```

Note: bokeh has to be installed manually, e.g., with `pip`:

```shell
$ pip3 install bokeh
```

## Design

See the [`ros2_tracing` design document](https://gitlab.com/ros-tracing/ros2_tracing/blob/master/doc/design_ros_2.md), especially the [*Goals and requirements*](https://gitlab.com/ros-tracing/ros2_tracing/blob/master/doc/design_ros_2.md#goals-and-requirements) and [*Analysis*](https://gitlab.com/ros-tracing/ros2_tracing/blob/master/doc/design_ros_2.md#analysis) sections.

## Packages

### ros2trace_analysis

Package containing a `ros2cli` extension to perform trace analysis.

### tracetools_analysis

Package containing tools for analyzing trace data.

See the [API documentation](https://ros-tracing.gitlab.io/tracetools_analysis-api/).
