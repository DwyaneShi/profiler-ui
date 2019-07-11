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

"""Utility methods for the TensorFlow Profiler UI."""
import os
import sys
import json
from tensorflow import gfile
from .constants import *

def get_timestamp(profile):
  with open(profile, 'r') as prof:
    prof_json = json.load(prof)
    for item in prof_json[PROFILE_ROOT]:
      if 'ts' in item.keys():
        return item['ts']

def get_informative_profile(folder):
  # Find the largest profile, since every step is profiled for the "graph"
  # view, and the largest step tends to be the most informative.
  # TODO: Optimize backend to only process largest step in this scenario.
  largest_profile_size = 0
  for file_name in gfile.ListDirectory(folder):
    if PROFILER_TMP_NAME in file_name:
      file_path = os.path.join(PROFILER_TMP_DIR, file_name)
      with gfile.GFile(file_path, 'rb') as profile:
        file_size = profile.size()
        if largest_profile_size < file_size:
          largest_profile_size = file_size
          prof_name = file_name
  return prof_name

def get_profile_by_timestamp(folder, ts):
  closest_ts = 0
  for file_name in gfile.ListDirectory(folder):
      if PROFILER_TMP_NAME in file_name:
        file_path = os.path.join(PROFILER_TMP_DIR, file_name)
        cur_ts = get_timestamp(file_path)
        if abs(ts - closest_ts) > abs(ts - cur_ts):
          closest_ts = cur_ts
          prof_name = file_name
  return prof_name

def get_first_profile_context(profile_dir):
  for prof in gfile.ListDirectory(profile_dir):
    profile_context = os.path.join(profile_dir, prof)
    if not os.path.isfile(profile_context):
      continue
    break
  return profile_context

def merge_profiles(profiles, merged_profile):
  merged_json = {PROFILE_ROOT: []}
  idx = 0
  for key in profiles:
    profile = profiles[key]
    id_prefix = idx << (sys.getsizeof(int()) - len(str(idx)))
    idx += 1
    with open(profile, 'r') as prof:
      prof_json = json.load(prof)
      for item in prof_json[PROFILE_ROOT]:
        if 'args' in item.keys():
          if 'name' in item['args'].keys():
            item['args']['name'] = key + ':' + item['args']['name']
          else:
            item['name'] = key + ':' + item['name']
        else:
          item['name'] = key + ':' + item['name']
        if 'pid' in item.keys():
          item['pid'] += id_prefix
        if 'id' in item.keys():
          item['id'] += id_prefix
        merged_json[PROFILE_ROOT].append(item)
  with open(merged_profile, 'w') as prof:
    json.dump(merged_json, prof)

def remove_tmp_files():
  """Removes temporary files created by the profiler."""
  for file_name in gfile.ListDirectory(PROFILER_TMP_DIR):
    if 'profiler-ui.' in file_name:
      gfile.Remove(os.path.join(PROFILER_TMP_DIR, file_name))

def prepare_tmp_dir():
  """Prepares a directory for temporary files created by the profiler."""
  if not gfile.Exists(PROFILER_TMP_DIR):
    gfile.MakeDirs(PROFILER_TMP_DIR)
  else:
    remove_tmp_files()
