#!/usr/bin/env python3
# _*_ coding: utf-8 _*_
import os
import subprocess
import sys
import time

command = ['echo', 'ok']
process: subprocess.Popen = None

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyFileSystemEventHander(FileSystemEventHandler):
    def __init__(self, fn):
        super(MyFileSystemEventHander, self).__init__()
        self.restart = fn

    def on_any_event(self, event):
        if event.src_path.endswith('.py'):
            print('Python source file changed: %s', event.src_path)
            self.restart()


def kill_process():
    global process
    if process:
        print('Kill process [%s]...' % process.pid)
        process.kill()
        process.wait()
        print('Process ended with code %s ' % process.returncode)


def start_process():
    global command, process
    print('Start process %s...' % ' '.join(command))
    process = subprocess.Popen(command, stdin=sys.stdin, stderr=sys.stderr, stdout=sys.stdout)
    pass


def restart_process():
    kill_process()
    start_process()


def start_watch(path, param):
    observer = Observer()
    observer.schedule(MyFileSystemEventHander(restart_process), path, recursive=True)
    observer.start()
    print('Watching directory %s...' % path)
    start_process()
    try:
        while True:
            time.sleep(0.5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == '__main__':
    argv = sys.argv[1:]
    if not argv:
        print('Usage: ./pymonitor.py your-script.py')
        exit(0)
    if argv[0] != 'python3':
        argv.insert(0, 'python3')
    command = argv
    path = os.path.abspath('.')
    start_watch(path, None)
