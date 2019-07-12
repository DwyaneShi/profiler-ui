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

"""Route handlers for the TensorFlow Profiler UI."""
import json
import os
import subprocess
from time import time as now
from .constants import *
from .utils import *
import flask
import tensorflow as tf
from tensorflow import gfile
from tensorflow.python import pywrap_tensorflow as pwtf
from tensorflow.python.pywrap_tensorflow import ProfilerFromFile
from tensorflow.python.pywrap_tensorflow import DeleteProfiler
from tensorflow.python.profiler import model_analyzer
from tensorflow.python.profiler import profile_context


def handle_loading_page(profile_path, profile_cnt):
  """Handles loading page requests."""
  return flask.render_template('loading.html')

def handle_home_page(profile_path, profile_cnt):
  """Handles home page requests."""
  return flask.render_template(
      'default.html', timestamp=now(), mdc_base_url=MDC_BASE_URL)

def handle_profile_api(profile_path, profile_cnt):
  """Handles profile API requests."""
  options = json.loads(flask.request.args.get('options'))

  # Determine view and output format.
  if options['view'] == 'pprof':
    output_format = 'pprof'
  elif options['view'] == 'graph':
    output_format = 'timeline'
  else:
    output_format = 'file'

  profile_dir = os.path.realpath(profile_path)
  resources_dir = os.path.join(profile_dir, 'resources')
  if not os.path.isdir(resources_dir):
    gfile.MkDir(os.path.join(profile_dir, 'resources'))

  if output_format == 'pprof':
    return produce_pprof_profile(profile_dir, resources_dir, profile_cnt, options)
  elif output_format == 'timeline':
    return produce_timeline_profile(profile_dir, resources_dir, profile_cnt, options)
  else:
    return produce_other_profile(profile_dir, resources_dir, profile_cnt, options)

def produce_pprof_profile(profile_dir, resources_dir, profile_cnt, options):
  image_path = os.path.join(resources_dir, PROFILER_PPROF_IMAGE_NAME)
  if not os.path.isfile(image_path):
    tmp_path = os.path.join(resources_dir, PROFILER_COMMON_PREFIX + options['view'])
    if not os.path.isfile(tmp_path):
      options['view'] = 'code'
      options['output'] = 'pprof:outfile=' + tmp_path
      opts = model_analyzer._build_options(options)  # pylint: disable=protected-access
      # Create profiler from the first profile context.
      profile_context = get_first_profile_context(profile_dir)
      ProfilerFromFile(profile_context.encode('utf-8'))
      pwtf.Profile(options['view'].encode('utf-8'), opts.SerializeToString())
      DeleteProfiler()

    """Produces a pprof profile."""
    subprocess.call([
        'pprof', '-svg', '--nodecount=100', '--sample_index=1',
        '-output={}'.format(image_path), tmp_path 
        ])
  return load_profile(image_path)

def produce_timeline_profile(profile_dir, resources_dir, profile_cnt, options):
  """Produces a timeline profile."""
  timeline_path = os.path.join(resources_dir, PROFILER_COMMON_PREFIX + 'timeline')
  if not os.path.isfile(timeline_path):
    profiles = {}
    log_path = os.path.join(PROFILER_TMP_DIR, PROFILER_TMP_NAME)
    options['output'] = 'timeline:outfile=' + log_path
    opts = model_analyzer._build_options(options)  # pylint: disable=protected-access
    for idx, prof in enumerate(gfile.ListDirectory(profile_dir)):
      prof_file = os.path.join(profile_dir, prof)
      if not os.path.isfile(prof_file):
        continue
      chosen_profile = os.path.join(resources_dir, PROFILER_COMMON_PREFIX + 'timeline_' + prof)
      profiles[prof] = chosen_profile
      if os.path.isfile(chosen_profile):
        if idx == 0:
          target_ts = get_timestamp(chosen_profile)
        continue
      tf.logging.info("Parse profile context %r" % prof_file)
      remove_tmp_files()
      # Parse profile context
      ProfilerFromFile(prof_file.encode('utf-8'))
      pwtf.Profile(options['view'].encode('utf-8'), opts.SerializeToString())
      DeleteProfiler()
      if idx == 0:
        prof_names = get_informative_profiles(PROFILER_TMP_DIR, profile_cnt)
        target_ts = get_timestamp(os.path.join(PROFILER_TMP_DIR, prof_names[0]))
      else:
        prof_names = get_profiles_by_timestamp(PROFILER_TMP_DIR, target_ts, profile_cnt)
      tf.logging.info("Choose %r as the most informative profile context for %r" % (prof_names, prof))
      gen_profile([os.path.join(PROFILER_TMP_DIR, name) for name in prof_names], chosen_profile)
    merge_profiles(profiles, timeline_path)
  return load_profile(timeline_path)

def produce_other_profile(profile_dir, resources_dir, profile_cnt, options):
  other_path = os.path.join(resources_dir, PROFILER_COMMON_PREFIX + options['view'])
  options['output'] = 'file:outfile=' + other_path
  opts = model_analyzer._build_options(options)  # pylint: disable=protected-access
  # Create profiler from the first profile context.
  profile_context = get_first_profile_context(profile_dir)
  ProfilerFromFile(profile_context.encode('utf-8'))
  pwtf.Profile(options['view'].encode('utf-8'), opts.SerializeToString())
  DeleteProfiler()

  return load_profile(other_path)

def load_profile(path):
  """Returns profile contents and removes temporary files."""
  if not gfile.Exists(path):
    return 'Profile was not generated.'

  with gfile.GFile(path, 'rb') as profile:
    response = profile.read()
  remove_tmp_files()
  return response
