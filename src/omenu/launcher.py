# launches applications 
import subprocess
import json

class Launcher:
    def __init__(self):
        self.process = None

    def launch(self, command):
        self.process = subprocess.Popen(command, shell=True)