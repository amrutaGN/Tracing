import sys
import os
from pathlib import Path
import json


def find_parent_span(span, spans):
    parent_span_id = None
    for reference in span.get('references', []):
        if reference.get('refType') == 'CHILD_OF':
            parent_span_id = reference.get('spanID')
            break
    if parent_span_id:
        parent_span = next((s for s in spans if s['spanID'] == parent_span_id), None)
        return parent_span
    return None


def climb_up_spans(span, spans):
    path = []
    while span:
        path.append(span)
        span = find_parent_span(span, spans)
    return path


os.makedirs('../injected/', exist_ok=True)

args = sys.argv

fileOrFolder = args[1]

call_graph = ["Service19", "Service7", "Service9", "Service17"]  # Predefined list of service names
error_injection_services = ["Service5", "Service10", "Service46"]  # Additional services for error injection

files = []
if os.path.isfile(fileOrFolder):
    files = [fileOrFolder]
elif os.path.isdir(fileOrFolder):
    files = Path(fileOrFolder).glob('*.json')

for file in files:
    data = json.load(open(file))
    fileName = os.path.split(file)[1]

    spans = data['data'][0]['spans']
    processes = data['data'][0]['processes']

    for span in spans:
        process_id = span['processID']
        service_name = processes.get(process_id, {}).get('serviceName')
        if service_name in call_graph:
            path = climb_up_spans(span, spans)
            for path_span in path:
                tags = path_span.get('tags', [])
                if len(tags) == 0:
                    path_span['tags'] = path_span.get('tags', []) + [
                        {
                            "key": "error",
                            "type": "bool",
                            "value": "true"
                        }
                    ]
        if service_name in error_injection_services:
            tags = span.get('tags', [])
            if len(tags) == 0:
                span['tags'] = span.get('tags', []) + [
                    {
                        "key": "error",
                        "type": "bool",
                        "value": "true"
                    }
                ]

    json.dump(data, open(f"../injected/{fileName}", 'w+'))

