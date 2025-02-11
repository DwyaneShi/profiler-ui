# TensorFlow Profiler UI

This is an enhanced version of the [TensorFlow Profiler (TFProf)](https://github.com/tensorflow/profiler-ui). With the enhanced TFProf, users are able to view multiple profile contexts on the same timeline page.

# Installation
1) Install Python dependencies.
   ```s
   pip install --user -r requirements.txt
   ```
2) Install [pprof](https://github.com/google/pprof#building-pprof).
3) Create a profile context file using the [tf.contrib.tfprof.ProfileContext](https://github.com/tensorflow/tensorflow/blob/v1.8.0/tensorflow/python/profiler/profile_context.py#L110-L148) class.
3) Start the UI.
   ```s
   python ui.py --profile_context_path=/path/to/your/profile/dir --successive_profile_context_count=3
   ```

# Learn more
You can learn more about the TensorFlow Profiler's Python API and CLI [here](https://github.com/tensorflow/tensorflow/blob/master/tensorflow/core/profiler/README.md#quick-start).

# Screenshot
<img src="docs/images/preview.png">

# Browser support
Currently only [Chrome](https://www.google.com/chrome/) is supported.
