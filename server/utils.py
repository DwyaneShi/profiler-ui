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
  max_ts = 0
  with open(profile, 'r') as prof:
    prof_json = json.load(prof)
    for item in prof_json[PROFILE_ROOT]:
      if 'ts' in item.keys():
        max_ts = max(max_ts, item['ts'])
  return max_ts

def get_informative_profiles(folder, cnt):
  # Find the largest profile, since every step is profiled for the "graph"
  # view, and the largest step tends to be the most informative.
  # TODO: Optimize backend to only process largest step in this scenario.
  file_sizes = []
  files = []
  for file_name in gfile.ListDirectory(folder):
    if PROFILER_TMP_NAME in file_name:
      file_path = os.path.join(PROFILER_TMP_DIR, file_name)
      with gfile.GFile(file_path, 'rb') as profile:
        file_size = profile.size()
        file_sizes.append(file_size)
        files.append(file_name)

  if cnt > 1:
    agg_file_sizes = []
    agg_size = 0
    for idx, file_size in enumerate(file_sizes):
      agg_size += file_size
      if idx >= cnt:
        agg_size -= file_sizes[idx - cnt]
      if idx >= cnt - 1:
        agg_file_sizes.append(agg_size)
  else:
    agg_file_sizes = file_sizes

  largest_agg_size = 0
  prof_idx = 0
  for idx, agg_size in enumerate(agg_file_sizes):
    if largest_agg_size < agg_size:
      largest_agg_size = agg_size
      prof_idx = idx
  return files[prof_idx:prof_idx+cnt]

def get_profiles_by_timestamp(folder, ts, cnt):
  closest_ts = 0
  files = []
  prof_idx = 0
  for file_name in gfile.ListDirectory(folder):
      if PROFILER_TMP_NAME in file_name:
        files.append(file_name)
        file_path = os.path.join(PROFILER_TMP_DIR, file_name)
        cur_ts = get_timestamp(file_path)
        if abs(ts - closest_ts) > abs(ts - cur_ts):
          closest_ts = cur_ts
          prof_idx = len(files) - 1
  return files[prof_idx:prof_idx+cnt]

def gen_profile(profiles, target_profile):
  if len(profiles) == 1:
    gfile.Copy(profiles[0], target_profile, True)
  else:
    target_json = {PROFILE_ROOT: []}
    process_mapping = {}
    id_start = 0
    for idx, profile in enumerate(profiles):
      id_max = 0
      pid_mapping = {}
      with open(profile, 'r') as prof:
        prof_json = json.load(prof)
        for item in prof_json[PROFILE_ROOT]:
          # create pid mapping. pids assigned to processes for different profiles are different
          if 'name' in item.keys() and item['name'] == PROFILE_PROCESS_TAG:
            if idx == 0:
              process_mapping[item['args']['name']] = item['pid']
            else:
              pid_mapping[item['pid']] = process_mapping[item['args']['name']]
          # reassign correct pid
          if idx > 0 and item['name'] != PROFILE_PROCESS_TAG and 'pid' in item.keys():
            item['pid'] = pid_mapping[item['pid']]
          if 'id' in item.keys():
            id_max = max(id_max, item['id'])
            item['id'] += id_start
          if idx == 0 or 'name' not in item.keys() or item['name'] != PROFILE_PROCESS_TAG:
            target_json[PROFILE_ROOT].append(item)
      id_start += id_max + 1
  with open(target_profile, 'w') as prof:
    json.dump(target_json, prof)

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
    id_prefix = idx << (sys.getsizeof(int()) - len(profiles.keys()))
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
