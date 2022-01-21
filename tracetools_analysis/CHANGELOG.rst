^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package tracetools_analysis
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

3.0.0 (2022-01-21)
------------------
* Update context_fields option name in profile example launch file
* Fix both rcl and rmw subscriptions being added to the rcl dataframe
* Support rmw pub/sub init and take instrumentation
* Support publishing instrumentation
* Change 'input_path' arg help message wording
* Add 'process --convert-only' option
* Deprecate 'convert' verb since it is just an implementation detail
* Simplify jupyter notebooks and add way to use Debian packages
* Contributors: Christophe Bedard

2.0.0 (2021-03-31)
------------------
* Set callback_instances' timestamp & duration cols to datetime/timedelta
* Improve performance by using lists of dicts as intermediate storage & converting to dataframes at the end
* Update callback_duration notebook and pingpong sample data
* Support instrumentation for linking a timer to a node
* Disable kernel tracing for pingpong example launchfile
* Support lifecycle node state transition instrumentation
* Contributors: Christophe Bedard

1.0.0 (2020-06-02)
------------------
* Add sphinx documentation for tracetools_analysis
* Improve RequiredEventNotFoundError message
* Add 'quiet' option to loading-related functions
* Declare dependencies on jupyter & bokeh, and restore pandas dependency
* Fix deprecation warnings by using executable instead of node_executable
* Define output metavar to simplify ros2 trace-analysis convert usage info
* Validate convert/process paths
* Add 'ip' context to example profiling launch file
* Switch to using ping/pong nodes for profile example launch file
* Add option to simply give an EventHandler when creating a DataModelUtil
* Do check before calling super().__init_\_()
* Add AutoProcessor and script entrypoint
* Make sure Processor is given at least one EventHandler
* Make do_convert_if_needed True by default
* Allow EventHandlers to declare set of required events
* Add cleanup method for ProcessingProgressDisplay
* Add memory usage analysis and entrypoint script
* Add callback-durations analysis script
* Contributors: Christophe Bedard, Ingo Lütkebohle

0.2.2 (2019-11-19)
------------------
* Update ROS 2 handler and data model after new tracepoint
* Fix timestamp column conversion util method
* Contributors: Christophe Bedard

0.2.0 (2019-10-14)
------------------
* Improve UX
* Add flag for process command to force re-conversion of trace directory
* Make process command convert directory if necessary
* Make output file name optional for convert command
* Remove references to "pickle" file and simply use "output" file
* Display Processor progress on stdout
* Add sample data, notebook, and launch file
* Add data model util functions
* Add profiling and CPU time event handlers
* Refactor and extend analysis architecture
* Contributors: Christophe Bedard

0.1.1 (2019-07-16)
------------------
* Update metadata
* Contributors: Christophe Bedard

0.1.0 (2019-07-11)
------------------
* Add analysis tools
* Contributors: Christophe Bedard, Ingo Lütkebohle
