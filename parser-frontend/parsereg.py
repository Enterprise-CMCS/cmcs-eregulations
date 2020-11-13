import os
import pathlib
from subprocess import Popen, PIPE
# from regparser.tasks import run_eregs_command

class ParseReg():
    def parse(self, api_key, title, part, output):
        # change directory
        parent = pathlib.Path.cwd().parent
        script_path = str(parent) + '/load_data.sh'
        # run load_data.sh
        script = [script_path, api_key, 'pipeline', title, part, output]
        print(script)
        out = Popen(script, stdout=PIPE, shell=True)
        return out.stdout.read()
