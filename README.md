# tracetools_analysis

Analysis tools for [ROS 2 tracing](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing).

## Setup

To display results, install:

* [Jupyter](https://jupyter.org/install)
* [Bokeh](https://bokeh.pydata.org/en/latest/docs/user_guide/quickstart.html#userguide-quickstart-install)

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

```
$ jupyter notebook
```

Then navigate to the [`analysis/`](./tracetools_analysis/analysis/) directory, and select one of the provided notebooks, or create your own!

For example:

```python
from tracetools_analysis import utils
from tracetools_analysis.loading import load_file
from tracetools_analysis.processor import Processor
from tracetools_analysis.processor.cpu_time import CpuTimeHandler
from tracetools_analysis.processor.ros2 import Ros2Handler

# Load converted trace file
events = load_file('/path/to/converted/file')

# Process
ros2_handler = Ros2Handler()
cpu_handler = CpuTimeHandler()

Processor(ros2_handler, cpu_handler).process(events)

# Use data model utils to extract information
ros2_util = utils.RosDataModelUtil(ros2_handler.data)
cpu_util = CpuTimeDataModelUtil(cpu_handler.data)

callback_durations = ros2_util.get_callback_durations()
time_per_thread = cpu_util.get_time_per_thread()
# ...

# Display, e.g. with bokeh or matplotlib
# ...
```

## Design

See the [`ros2_tracing` design document](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing/blob/master/doc/design_ros_2.md), especially the [*Goals and requirements*](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing/blob/master/doc/design_ros_2.md#goals-and-requirements) and [*Analysis architecture*](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing/blob/master/doc/design_ros_2.md#analysis-architecture) sections.
