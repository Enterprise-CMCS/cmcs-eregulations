import sys
import json

j = json.loads(sys.stdin.read())
print(j)
sys.exit(1 if 'FunctionError' in j else 0)
