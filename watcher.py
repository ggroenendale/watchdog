import os
import sys
import time
import yaml
import contextlib
from pprint import pprint
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
# import logging
# from watchdog.events import LoggingEventHandler

# This file will watch a directory for file changes and will automatically run code

writing = False

class PausableObserver(Observer):
    def dispatch_events(self, *args, **kwargs):
        if not getattr(self, '_is_paused', False):
            super(PausableObserver, self).dispatch_events(*args, **kwargs)
    
    def pause(self):
        self._is_paused = True
        
    def resume(self):
        time.sleep(self.timeout)
        self.event_queue.queue.clear()
        self._is_paused = False
        
    @contextlib.contextmanager
    def ignore_events(self):
        self.pause()
        yield
        self.resume()

class AutoIncrement(FileSystemEventHandler):
    # Construct the class and create Properties
    def __init__(self):
        self.configs = ''
        self.globs = []
        self.load_config()
    
    # Define the method that will run if watchdog detects a change
    def on_modified(self, event):
        global writing
        with observer.ignore_events():
            print(f'Saw file was saved! Type:{event.event_type}')
            print('Checking File Flag...')
            if writing is False:
                print("Its ok to run the code we are not writing files")
                self.file_test()
            else:
                print("Looks like we are writing files so lets not fuck it up.")
                return
        
    # Define glob parameters based on config file and used filetypes   
    def load_config(self):
        conffile = os.path.join(os.path.dirname(__file__), 'config.yml')
        self.configs = yaml.safe_load(open(conffile))
        for directories in self.configs['directories']:
            for types in self.configs['filetypes']:
                self.globs.append(f'{directories}/**/*{types}')
        # pprint(configs)
        
    # Loop through all possible globs
    def file_test(self):
        path = sys.argv[1] if len(sys.argv) > 1 else '.'
        # Handle only the files listed in the config for directories[]
        # and those files where comments can be edited by this python file
        for glob in self.globs:
            # for filetypes in self.configs['filetypes']:
            #     directory = Path(path).glob(f'{directories}/**/*.php')
            # print(glob)
            directory = Path(path).glob(glob)
            pprint(glob)
            for file in directory:
                filename = str(file)
                print(filename)
                self.open_file(filename)
                
    def open_file(self, script_file):
        global writing
        writing = True
        if ".php" in script_file:
            # print(f'{script_file} is a PHP file')
            code = []
            with open(script_file, mode='r') as in_file:
                code = in_file.readlines()
                in_file.close()
            # Sort through the code and make changes
            if len(code) > 1:
                # First grab the beginning <?php tag
                line_one = code[0]
                
                # Next build the documentation block
                documentation = [
                    "//-- The beginning of the documentation block\n",
                    "//-- Which will look something like this\n",
                    "//-- And may have special characters to find the beginning\n",
                    "//-- And end\n"
                ]
                
                # Now loop through the code list and determine if any
                # elements should be skipped
                code_remainder = []
                for line in code:
                    if "<?php" in line:
                        print("skipping line")
                    elif "//--" in line:
                        print("Skipping current documentation")
                    else:
                        code_remainder.append(line)
                        
                # Create a new list complete with the open tag, the documentation
                # block, and the remainder of the code
                code_out = []
                code_out.append(line_one)
                code_out.extend(documentation)
                code_out.extend(code_remainder)
                
                # Now rewrite the file
                with open(script_file, mode='w') as out_file:
                    out_file.writelines(code_out)
                    # for i in range(len(code)):
                        # print(f'Writing line {i+1}: {code[i]}')
                        # out_file.writelines("%s" %(code[i]))
                    out_file.close()
                pprint(code)
            else:
                print("This file has 0 lines")
            # ReWrite the file
                
                # for lines in code:
                #     print(lines)
        if ".js" in script_file:
            print(f'{script_file} is a JavaScript file')
        if ".py" in script_file:
            print(f'{script_file} is a Python file')
        if ".css" in script_file:
            print(f'{script_file} is a CSS file')
        # with open(script_file, 'w') as file:
        #     code = file.readlines()
        #     print(code[0])
        #     # for lines in code:
        #     #     print(lines)
        writing = False
        

if __name__ == "__main__":
    # logging.basicConfig(filename="watchdog.log", level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    path = sys.argv[1] if len(sys.argv) > 1 else '.'
    observer = PausableObserver()
    event_handler = AutoIncrement()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()