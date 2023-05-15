import sys
import os
from pathlib import Path
import json 
import random

os.makedirs('../injected/', exist_ok=True)

args = sys.argv

fileOrFolder = args[1]
min_err_prcnt = int(args[2])
max_err_prcnt = int(args[3])


files = []
if os.path.isfile(fileOrFolder):
    files = [fileOrFolder]

elif os.path.isdir(fileOrFolder):
    files = Path(fileOrFolder).glob('*.json')

for file in files:
    err_prcnt = random.randrange(min_err_prcnt, max_err_prcnt+1)
    data = json.load(open(file))
    fileName = os.path.split(file)[1]

    # get specific tag
    # check if there is error already
    # inject error accordingly
    for span in data['data'][0]['spans']:
        # check if there are tags
        if span.get('tags') is not None:
            # check if there are error tags
            for tag in span.get('tags'):
                # has error = true
                if tag.get('key') == 'error' and tag.get('type') == 'bool' and tag.get('value') == 'true':
                    continue
                else:
                    if random.random() < err_prcnt / 100:
                        span['tags'].append(
                            [
                                {
                                    "key": "error",
                                    "type": "bool",
                                    "value": "true"
                                }
                            ]
                        )
        else:
            if random.random() < err_prcnt / 100:
                    span['tags'] = [
                        {
                            "key": "error",
                            "type": "bool",
                            "value": "true"
                        }
                    ]

    json.dump(data,open(f"../injected/{fileName}",'w+'))