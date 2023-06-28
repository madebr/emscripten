#!/usr/bin/env python3
"""Bootstrap script for emscripten developers / git users.

After checking out emscripten there are certain steps that need to be
taken before it can be used.  This script enumerates and automates
these steps and is able to run the just the steps that are needed
based on the timestamps of various input files (kind of like a dumb
version of a Makefile).
"""
import argparse
import os
import shutil
import sys

__rootdir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, __rootdir__)

STAMP_DIR = os.path.join(__rootdir__, 'out')

from tools import shared, utils

actions = [
  ('npm packages', 'package.json', [shutil.which('npm'), 'ci']),
  ('create entry points', 'tools/maint/create_entry_points.py', [sys.executable, 'tools/maint/create_entry_points.py'])
]


def check():
  for name, filename, _ in actions:
    stamp_file = os.path.join(STAMP_DIR, os.path.basename(filename) + '.stamp')
    filename = utils.path_from_root(filename)
    if not os.path.exists(stamp_file) or os.path.getmtime(filename) > os.path.getmtime(stamp_file):
      utils.exit_with_error(f'emscripten setup is not complete ("{name}" is out-of-date). Run bootstrap.py to update')


def main(args):
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument('-v', '--verbose', action='store_true', help='verbose', default=False)
  parser.add_argument('-n', '--dry-run', action='store_true', help='dry run', default=False)
  args = parser.parse_args()

  for name, filename, cmd in actions:
    filename = utils.path_from_root(filename)
    stamp_file = os.path.join(STAMP_DIR, os.path.basename(filename) + '.stamp')
    if os.path.exists(stamp_file) and os.path.getmtime(filename) <= os.path.getmtime(stamp_file):
      print('Up-to-date: %s' % name)
      continue
    print('Out-of-date: %s' % name)
    if args.dry_run:
      print(' (skipping: dry run) -> %s' % ' '.join(cmd))
      return
    print(' -> %s' % ' '.join(cmd))
    shared.run_process(cmd)
    utils.safe_ensure_dirs(STAMP_DIR)
    utils.write_file(stamp_file, 'Timestamp file created by bootstrap.py')


if __name__ == '__main__':
  main(sys.argv[1:])
