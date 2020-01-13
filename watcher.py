import os
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import LoggingEventHandler
from watchdog.events import FileSystemEventHandler

# This file will watch a directory for file changes and will automatically run code

class AutoIncrement(FileSystemEventHandler):
    def on_modified(self, event):
        print(f'Saw file was saved! {event.event_type}')
        # return super().on_modified(event)

if __name__ == "__main__":
    logging.basicConfig(filename="watchdog.log", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    event_handler = AutoIncrement()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()