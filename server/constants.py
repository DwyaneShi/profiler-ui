# Copyright 2018 Google Inc. All Rights Reserved.
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

"""Constants for the TensorFlow Profiler UI."""
import os

# Locations for temporary files.
PROFILER_TMP_DIR = '/tmp/tensorflow/profiler'
PROFILER_COMMON_PREFIX = 'profiler-ui.'
PROFILER_TMP_NAME = PROFILER_COMMON_PREFIX + 'tmp'
PROFILER_PPROF_IMAGE_NAME = PROFILER_COMMON_PREFIX + 'pprof.png'

PROFILE_ROOT = 'traceEvents'
PROFILE_PROCESS_TAG = 'process_name'

# Limits on computation per trace.
MAX_SERVING_SECS = 60 * 60
MAX_TRACING_SECS = 300
TRACE_STEPS = 5

# Location and version of Material library.
MDC_BASE_URL = 'https://unpkg.com/material-components-web@0.20.0/dist/'
