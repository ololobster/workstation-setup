#!/usr/bin/python
# Dumb & easy to use job scheduler.
# Run some jobs:
# $ scheduler.py run job1 'make bookworm.libvirt'
# $ scheduler.py run job2 'make bookworm.vbox'
# $ scheduler.py run job3 'make redos8.libvirt'
# See the result:
# $ scheduler.py report
# See the 1st job's output:
# cat /tmp/scheduler/output/job1
# Clean the logs:
# $ scheduler.py clean

import argparse
from pathlib import Path
import pty
import shutil
import subprocess
import sys

DEFAULT_TARGET_DIR = '/tmp/scheduler'
RUN_COMMAND = 'run'
REPORT_COMMAND = 'report'
CLEAN_COMMAND = 'clean'


def run_job(args):
    target_dir_path = Path(DEFAULT_TARGET_DIR)
    output_dir_path = target_dir_path / 'output'
    if not target_dir_path.is_dir():
        target_dir_path.mkdir()
    if not output_dir_path.is_dir():
        output_dir_path.mkdir()
    rc_file_path = target_dir_path / args.name
    if rc_file_path.exists():
        print('Fail. Clean first.')
        sys.exit(1)

    # master_fd, slave_fd = pty.openpty()
    subprocess_kwargs = {'shell': True}
    if not args.without_logs:
        log_file_path = output_dir_path / args.name
        log_file = open(log_file_path, 'w')
        subprocess_kwargs['stdout'] = log_file
        subprocess_kwargs['stderr'] = log_file
    rc = subprocess.call(args.job, **subprocess_kwargs)
    with open(rc_file_path, 'w') as rc_file:
        rc_file.write(str(rc))
    print(f'Job {args.name} is finished.')

def print_report(args):
    target_dir_path = Path(DEFAULT_TARGET_DIR)
    if not target_dir_path.is_dir():
        print('Fail. Run some jobs first.')
        sys.exit(1)

    success_count = 0
    fail_count = 0
    for rc_file_path in target_dir_path.iterdir():
        if not rc_file_path.is_file():
            continue
        job_name = rc_file_path.name
        rc = rc_file_path.read_text()
        if rc == '0':
            success_count += 1
            print(f'{job_name}: success.')
        else:
            fail_count +=1
            print(f'{job_name}: fail (return code {rc}).')
    print(f'Success: {success_count}, fail: {fail_count}.')


def clean_target_dir(args):
    target_dir_path = Path(DEFAULT_TARGET_DIR)
    if target_dir_path.is_dir():
        shutil.rmtree(target_dir_path)
    print('Cleaning was finished.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='scheduler.py')
    subparsers = parser.add_subparsers(help='A command', dest='command')
    run_parser = subparsers.add_parser(RUN_COMMAND, help='Run a job')
    run_parser.add_argument('name', type=str, help='Job\'s name')
    run_parser.add_argument('job', type=str, help='shell command to execute')
    run_parser.add_argument('--without-logs', action='store_true', default=False)
    report_parser = subparsers.add_parser(REPORT_COMMAND, help='Print a report')
    clean_parser = subparsers.add_parser(CLEAN_COMMAND, help='Clean the logs')
    args = parser.parse_args()

    if args.command == RUN_COMMAND:
        run_job(args)
    elif args.command == REPORT_COMMAND:
        print_report(args)
    elif args.command == CLEAN_COMMAND:
        clean_target_dir(args)
