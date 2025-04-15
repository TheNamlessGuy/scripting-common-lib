import subprocess

def repo_root(*, cwd = None, decode_format = 'utf-8'):
  return subprocess.run(['git', 'rev-parse', '--show-toplevel'], stdout = subprocess.PIPE, cwd = cwd).stdout.decode(decode_format).strip()