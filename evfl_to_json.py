#!/usr/bin/env python
from evfl import EventFlow
from evfl.repr_util import generate_flowchart_graph
from pathlib import Path
import json
import sys


file = Path(sys.argv[1])
flow = EventFlow()
with open(file, "rb") as f:
    flow.read(f.read())

json_obj = json.dumps(generate_flowchart_graph(flow), indent=4, default=lambda x: str(x))

with open(file.with_suffix(".json"), "w") as out:
    out.write(json_obj)