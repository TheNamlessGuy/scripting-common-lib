#!/usr/bin/python3

import os
import json
import subprocess

common_root = subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout = subprocess.PIPE, cwd = os.path.dirname(os.path.realpath(__file__))).stdout.decode('utf-8').strip()
plugin_root = os.path.dirname(common_root)
filename = os.path.join(plugin_root, os.path.basename(plugin_root) + '.zip')
if os.path.exists(filename):
  if not os.path.isfile(filename):
    print("'{0}' exists but isn't a file. Unsure how to proceed")
    exit(1)

  while True:
    response = input("'{0}' already exists. Should it be removed? [y/n] ".format(filename))
    if response == 'y':
      print("Removing file '{0}'...".format(filename))
      os.remove(filename)
      break
    elif response == 'n':
      print("Cannot continue while old file still exists")
      exit(0)

files = [
  os.path.join(plugin_root, 'res'),
  os.path.join(plugin_root, 'src'),
  os.path.join(plugin_root, 'manifest.json'),
]

with open(os.path.join(plugin_root, 'manifest.json'), 'r') as f:
  common_scripts = json.loads(f.read())
  common_scripts = [os.path.join(plugin_root, x) for x in common_scripts['background']['scripts']]
  common_scripts = [x for x in common_scripts if x.startswith(common_root)]
  files += common_scripts

files = [os.path.relpath(x, plugin_root) for x in files]

print("Creating file '{0}'...".format(filename))
subprocess.run(['zip', '-r', '-q', filename] + files, cwd = plugin_root)