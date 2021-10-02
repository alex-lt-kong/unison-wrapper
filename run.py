#!/usr/bin/python3

import click
import os
import pathlib
import json

log_dir = ''
profile_dir = ''
unison_path = ''

def load_settings():

  global log_dir, unison_path, profile_dir
  with open('settings.json', 'r') as f:
    data = json.load(f)
  unison_path = data['unison_path']
  profile_dir = data['profile_dir']
  log_dir = data['log_dir']

@click.command()
@click.option('--manual', is_flag=True, help='unison will ask users to confirm before starting file transfer')
@click.option('--timer', is_flag=True, help='print elapsed time at the end of synchronization')
def main(manual: bool, timer: bool):

  load_settings()

  if os.path.isfile(unison_path) is False:
    print(f'Unison not found at [{unison_path}]')
  if os.path.isdir(profile_dir) is False:
    print(f'Unison profiles directory [{profile_dir}] does not exist')
  if os.path.isdir(log_dir) is False:
    print(f'Log directory [{log_dir}] does not exist')

if __name__ == '__main__':
  main()