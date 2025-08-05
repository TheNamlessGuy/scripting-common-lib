import os
import re
import json
import subprocess

from . import print

class SrtEntry:
  @classmethod
  def read_file(cls, abspath, *, encoding = 'utf-8'):
    with open(abspath, 'r', encoding = encoding) as f:
      contents = f.read().split('\n\n')
      return [SrtEntry(x) for x in contents if x.strip() != '']

  @classmethod
  def write_file(cls, srts, abspath, *, encoding = 'utf-8'):
    contents = '\n\n'.join([srt.print() for srt in srts])
    with open(abspath, 'w', encoding = encoding) as f:
      f.write(contents)

  def __init__(self, str):
    str = str.split('\n')
    self.idx = str[0]
    times = str[1].split(' --> ')
    self.startTime = times[0]
    self.endTime = times[1]
    self.lines = str[2:]

  def print(self):
    return self.idx + '\n' + self.startTime + ' --> ' + self.endTime + '\n' + '\n'.join(self.lines)

  def maxlen(self):
    return len(self.print().split('\n')[1]) + 3 # The length of the "times" line + 3 is the max length

def find_sub_files_for(path, ends = ['.srt']):
  retval = []

  path_split = os.path.splitext(path)
  prefix = os.path.basename(path_split[0])
  dirname = os.path.dirname(os.path.abspath(path))

  for entry in os.listdir(dirname):
    entry_split = os.path.splitext(entry)
    if entry_split[1] in ends and entry_split[0].startswith(prefix):
      retval.append(entry)

  return retval

def has_subfiles(path, ends = ['.srt']):
  return len(find_sub_files_for(path, ends = ends)) > 0

def get_language_and_title_from_sub_file(subfile, videofile, *, default_lang = None, default_title = None):
  videofile_split = os.path.splitext(videofile)
  prefix = os.path.basename(videofile_split[0])

  subfile_split = os.path.splitext(subfile)
  data = subfile_split[0][len(prefix):]
  while data.startswith('.'):
    data = data[1:]
  data = data.split('.')

  if len(data[0]) > 0:
    lang = data[0]
  elif default_lang is not None:
    lang = default_lang
  else:
    lang = ''

  if len(data) > 1 and len(data[1]) > 0:
    title = data[1]
  elif default_title is not None:
    title = default_title
  else:
    title = ''

  return [lang, title]

def get_streams_from(file, *, whitelisted_languages = None):
  retval = []

  output = subprocess.run(['ffprobe', '-v', '0', '-select_streams', 's', '-show_entries', 'stream=index', '-show_entries', 'stream_tags=language,handler_name,title', '-of', 'json', file], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
  output = json.loads(output.stdout)

  retval = []
  for entry in output['streams']:
    if 'tags' not in entry: entry['tags'] = {}

    if 'handler_name' in entry['tags'] and entry['tags']['handler_name'] not in ['SubtitleHandler']:
      print.fatal_error("subs::get_sub_data fatal error 1: unsupported handler_name")

    retval.append({
      'index': entry['index'],
      'title': entry['tags']['title'] if 'title' in entry['tags'] else None,
      'language': entry['tags']['language'] if 'language' in entry['tags'] else None,
    })

  return retval

_font_start_regex = re.compile(r'<font[^>]+>')
_font_end_regex = re.compile(r'</font>')
def extract_stream_to_file(file, stream, *, filetype = 'srt', remove_font_tags = True):
  file = os.path.realpath(file)
  filename = os.path.splitext(os.path.basename(file))[0]

  base_output_file = filename
  if stream['language'] is not None: base_output_file += '.{0}'.format(stream['language'])
  if stream['title'] is not None: base_output_file += '.{0}'.format(stream['title'])

  idx = 0
  output_file = base_output_file + '.' + filetype
  while os.path.isfile(output_file):
    output_file = base_output_file + '.' + str(idx + 1) + '.' + filetype
    idx += 1
  output_file = os.path.join(os.path.dirname(file), output_file)

  data = subprocess.run(['ffmpeg', '-v', '0', '-i', file, '-map', '0:' + str(stream['index']), '-f', filetype, '-'], stdout = subprocess.PIPE, stderr = subprocess.PIPE).stdout

  data = data.decode().strip().split('\n')
  if remove_font_tags:
    for l in range(len(data)):
      data[l] = _font_start_regex.sub('', data[l])
      data[l] = _font_end_regex.sub('', data[l])
  data = '\n'.join(data).encode('utf-8')

  with open(output_file, 'wb') as f:
    f.write(data)

  return output_file
