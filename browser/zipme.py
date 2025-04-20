#!/usr/bin/python3

import os
import sys
import json
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))) # Fuck you python, you terrible fucking language

from python import files
from python import git
from python import input

common_root = git.repo_root(cwd = files.cwd(for_path = __file__))
plugin_root = os.path.dirname(common_root)
rel_filename = os.path.basename(plugin_root) + '.zip'
filename = os.path.join(plugin_root, rel_filename)
if os.path.exists(filename):
  if not os.path.isfile(filename):
    print("'{0}' exists but isn't a file. Unsure how to proceed")
    exit(1)

  shouldRemove = input.confirm("'{0}' already exists. Should it be removed?".format(rel_filename))
  if shouldRemove:
    print("Removing file '{0}'...".format(rel_filename))
    os.remove(filename)
  else:
    print("Cannot continue while old file still exists")
    exit(0)

files = [
  os.path.join(plugin_root, 'res'),
  os.path.join(plugin_root, 'src'),
  os.path.join(plugin_root, 'manifest.json'),
]

with open(os.path.join(plugin_root, 'manifest.json'), 'r') as f:
  manifest = json.loads(f.read())

  if 'background' in manifest and 'scripts' in manifest['background']:
    common_scripts = [os.path.join(plugin_root, x) for x in manifest['background']['scripts']]
    common_scripts = [x for x in common_scripts if x.startswith(common_root)]
    files += common_scripts

  if 'browser_specific_settings' in manifest and 'namless' in manifest['browser_specific_settings'] and 'common_includes' in manifest['browser_specific_settings']['namless']:
    files += [os.path.join(common_root, x) for x in manifest['browser_specific_settings']['namless']['common_includes']]

# Just in case
fail = False
for file in files:
  if not os.path.exists(file):
    print("'{0}' does not exist".format(file))
    fail = True
if fail:
  exit(1)

files = [os.path.relpath(x, plugin_root) for x in files]
print("Creating file '{0}'...".format(rel_filename))
subprocess.run(['zip', '-r', '-q', filename] + files, cwd = plugin_root)