#!/usr/bin/python3

from typing import Tuple
import click
import json
import logging
import os
import pathlib
import subprocess
import sys


log_path = ''
unison_path = ''
roots_prefix = []

def load_and_check_settings() -> bool:
  
  global log_path, roots_prefix, unison_path
  with open(os.path.join(sys.path[0], 'settings.json'), 'r') as f:
    data = json.load(f)
  unison_path = data['unison_path']
  log_path = os.path.join(data['log_dir'], 'local-sync.log')
  roots_prefix = data['local_sync']['roots_prefix']

  if os.path.isfile(unison_path) is False:
    print(f'Unison not found at [{unison_path}]')
    return False

  return True


def load_roots() -> Tuple[list[str], list[str]]:

  root1, root2 = [], []
  assert len(root1) == len (root2)
  with open(os.path.join(sys.path[0], 'settings.json'), 'r') as f:
    data = json.load(f)
    for pair in data['local_sync']['roots']:
      root1.append(os.path.join(pathlib.Path.home(), roots_prefix[0], pair[0]))
      root2.append(os.path.join(pathlib.Path.home(), roots_prefix[1], pair[1]))
      logging.debug(f'Adding root pair {root1[-1]}, {root2[-1]}')
  
  return root1, root2


@click.command()
@click.option('--debug', is_flag=True, help='Enable debug mode (Unison will print a LOT of information!)')
@click.option('--manual', is_flag=True, help='Unison will ask users to confirm before starting file transfer')
def main(debug: bool, manual: bool):

  logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG if debug else logging.INFO,
    format='%(asctime)s %(levelname)06s - %(funcName)s: %(message)s',
    datefmt='%Y%m%d-%H%M%S',
  )
  logging.info(f'Unison wrapper for local synchronization started')

  root1, root2 = load_roots()
  
  for i in range(len(root1)):
    unison_cmd = [unison_path, root1[i], root2[i], '-auto', '-contactquietly', '-logfile', log_path]
    
    # -auto  automatically accept default (nonconflicting) actions
    if manual:
      unison_cmd.extend(['-batch=false', '-silent=false'])
    else:
      unison_cmd.extend(['-batch=true', '-silent=true'])
    msg = f'{i}-th pair\'s sync about to start--[{root1[i]}] and [{root2[i]}]'
    logging.info(msg)
    if manual:
      print(msg)
    logging.debug(f'Command about to be executed: {unison_cmd}')
    p = subprocess.Popen(args=unison_cmd)
    p.communicate()
    if p.returncode != 0:
      err_message = f'{i}-th pair\'s sync exited with {p.returncode=}'
      print("\n" + err_message)
      logging.error(err_message)
    else:
      msg = f'{i}-th pair\'s sync exited with {p.returncode=}'
      logging.info(msg)
      if manual:
        print(msg)
  logging.info(f'Unison wrapper for local sync exited')


if __name__ == '__main__':
  if load_and_check_settings() is False:
    exit(1)
  main()
