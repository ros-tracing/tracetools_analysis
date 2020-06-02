# tracetools_analysis

[![pipeline status](https://gitlab.com/micro-ROS/ros_tracing/tracetools_analysis/badges/master/pipeline.svg)](https://gitlab.com/micro-ROS/ros_tracing/tracetools_analysis/commits/master)

Analysis tools for [ROS 2 tracing](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing).

## Trace analysis

After generating a trace (see [`ros2_tracing`](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing#tracing)), we can analyze it to extract useful execution data.

### Commands

Since CTF traces (the output format of the [LTTng](https://lttng.org/) tracer) are very slow to read, we first convert them into a single file which can be read much faster.

```
$ ros2 trace-analysis convert /path/to/trace/directory
```

Then we can process it to create a data model which could be queried for analysis.

```
$ ros2 trace-analysis process /path/to/trace/directory
```

### Jupyter

The last command will process and output the raw data models, but to actually display results, process and analyze using a Jupyter Notebook.

```shell
$ jupyter notebook
```

Then navigate to the [`analysis/`](./tracetools_analysis/analysis/) directory, and select one of the provided notebooks, or create your own!

For example:

```python
from tracetools_analysis import loading
from tracetools_analysis import processor
from tracetools_analysis import utils

# Load trace directory or converted trace file
events = loading.load_file('/path/to/trace/or/converted/file')

# Process
ros2_handler = processor.Ros2Handler()
cpu_handler = processor.CpuTimeHandler()

processor.Processor(ros2_handler, cpu_handler).process(events)

# Use data model utils to extract information
ros2_util = utils.ros2.Ros2DataModelUtil(ros2_handler.data)
cpu_util = utils.cpu_time.CpuTimeDataModelUtil(cpu_handler.data)

callback_durations = ros2_util.get_callback_durations()
time_per_thread = cpu_util.get_time_per_thread()
# ...

# Display, e.g. with bokeh or matplotlib
# ...
```

Note: bokeh has to be installed manually, e.g. with `pip`:

```shell
$ pip3 install bokeh
```

## Design

See the [`ros2_tracing` design document](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing/blob/master/doc/design_ros_2.md), especially the [*Goals and requirements*](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing/blob/master/doc/design_ros_2.md#goals-and-requirements) and [*Analysis*](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing/blob/master/doc/design_ros_2.md#analysis) sections.

## Packages

### ros2trace_analysis

Package containing a `ros2cli` extension to perform trace analysis.

### tracetools_analysis

Package containing tools for analyzing trace data.

See the [API documentation](https://micro-ros.gitlab.io/ros_tracing/tracetools_analysis-api/).
