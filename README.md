# tracetools_analysis

Analysis tools for [ROS 2 tracing](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing).

## Setup

To display results, install:

* [Jupyter](https://jupyter.org/install)
* [Bokeh](https://bokeh.pydata.org/en/latest/docs/user_guide/quickstart.html#userguide-quickstart-install)

## Trace analysis

After generating a trace (see [`ros2_tracing`](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing#tracing)), we can analyze it to extract useful execution data.

Since CTF traces (the output format of the [LTTng](https://lttng.org/) tracer) are very slow to read, we first convert them into a single file which can be read much faster.

```
$ ros2 trace-analysis convert /path/to/trace/directory
```

Then we can process it to create a data model which could be queried for analysis.

```
$ ros2 trace-analysis process /path/to/trace/directory
```

This last command will process and output the raw data models, but to actually display results, process and analyze using a Jupyter Notebook.

```
$ jupyter notebook
```

Then navigate to the [`analysis/`](./tracetools_analysis/analysis/) directory, and select one of the provided notebooks, or create your own!

## Design

See the [`ros2_tracing` design document](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing/blob/master/doc/design_ros_2.md), especially the [*Goals and requirements*](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing/blob/master/doc/design_ros_2.md#goals-and-requirements) and [*Analysis architecture*](https://gitlab.com/micro-ROS/ros_tracing/ros2_tracing/blob/master/doc/design_ros_2.md#analysis-architecture) sections.
