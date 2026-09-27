# launches applications 
import subprocess
import json

class Launcher:
    def __init__(self):
        self.process = None
        with open('config.json') as f:
            self.config = json.load(f)

    def launch(self, command):
        self.process = subprocess.Popen(command, shell=True)