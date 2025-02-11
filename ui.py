#!/usr/bin/env python

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

"""CLI for the TensorFlow Profiler UI."""
import os
import sys
from server.server import start_server
import tensorflow as tf
from tensorflow import flags


# Define flags.
FLAGS = flags.FLAGS
flags.DEFINE_integer('server_port', 7007, 'Flask server port.')
flags.DEFINE_string('profile_context_path', '', 'Path to profile context.')
flags.DEFINE_integer('successive_profile_context_count', 1, 'The number of successive profile contexts to show.')
flags.DEFINE_boolean('browser', True, 'Open browser after startup.')


def main(_):
  profile_path = os.path.expanduser(FLAGS.profile_context_path)
  profile_cnt = FLAGS.successive_profile_context_count

  # Require "profile_context_path" flag.
  if not profile_path:
    sys.stderr.write('Please provide a value for "profile_context_path".\n')
    return

  # Verify profile context file exists.
  if not os.path.isdir(profile_path):
    sys.stderr.write('No directory was found at "{}".\n'.format(profile_path))
    return

  # Start server.
  start_server(profile_path, profile_cnt, FLAGS.server_port, FLAGS.browser)


if __name__ == '__main__':
  tf.app.run()
