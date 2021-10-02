#!/usr/bin/python3

import click
import json
import logging
import os
import subprocess
import time

log_dir = ''
unison_path = ''


def load_and_check_settings():

  global log_dir, unison_path, profile_dir
  with open('settings.json', 'r') as f:
    data = json.load(f)
  unison_path = data['unison_path']
  log_dir = data['log_dir']

  if os.path.isfile(unison_path) is False:
    print(f'Unison not found at [{unison_path}]')
    return
  if os.path.isdir(log_dir) is False:
    print(f'Log directory [{log_dir}] does not exist')
    return

@click.command()
@click.option('--debug', is_flag=True, help='Enable debug mode (Unison will print a LOT of information!)')
@click.option('--manual', is_flag=True, help='Unison will ask users to confirm before starting file transfer')
@click.option('--timer', is_flag=True, help='Print elapsed time at the end of synchronization')
@click.option('--profile', required=True, type=str, help='Name of Unison profile in profile_dir EXCLUDING .prf')
def main(debug: bool, manual: bool, timer: bool, profile: str):

  log_path = os.path.join(log_dir, profile)
  logging.basicConfig(
      filename=log_path,
      level=logging.DEBUG if debug else logging.INFO,
      format=('%(asctime)s %(levelname)s %(module)s-%(funcName)s: %(message)s'),
      datefmt='%Y-%m-%d %H:%M:%S',
  )
  logging.info(f'Unison wrapper started')
  if debug:
    logging.debug(f'Debug mode enabled')

  unison_cmd = [unison_path]
  if manual:
    unison_cmd.extend(['-batch=false', '-silent=false'])
    # https://www.cis.upenn.edu/~bcpierce/unison/download/releases/stable/unison-manual.html
    # -batch             batch mode: ask no questions at all
    # -silent            print nothing except error messages
  if debug:
    unison_cmd.extend(['-debug', 'all'])
    # -debug xxx         debug module xxx ('all' -> everything, 'verbose' -> more)
  unison_cmd.extend(['-logfile', log_path])
  
  unison_cmd.append(os.path.join('profiles/' + profile))
  logging.debug(f'{unison_cmd}')
  start = time.time()
  p = subprocess.Popen(args=unison_cmd)
  stdout, stderr = p.communicate()
  if p.returncode == 0:
    # the most common scenario is synchronization conflict: Unison will
    # print the conflict item WITHOUT a \n at the end, so we add one to it.
    logging.info(f'Unison exited with {p.returncode=}')
  else:
    print(f'\nUnison exited with {p.returncode=}')
    logging.error(f'Unison exited with {p.returncode=}')
  if timer:
    print(f'Elapsed time: {(time.time() - start) / 60:,.1f} minutes')
  

if __name__ == '__main__':

  if load_and_check_settings() is False:
    exit(1)
  main()
