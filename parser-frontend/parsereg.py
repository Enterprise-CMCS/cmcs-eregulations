import os
from subprocess import Popen, PIPE

class ParseReg():
    def parse(self, api_key, title, part, output):
        # change directory
        source = os.path.dirname(__file__)
        parent = os.path.join(source, '../')
        script_path = os.path.join(parent, 'load_data.sh')
        # run load_data.sh
        script = [script_path, api_key, 'pipeline', title, part, output]
        print(script)
        out = Popen(script, stdout=PIPE, shell=True)
        return out.stdout.read()
