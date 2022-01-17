#!/usr/bin/env python
from evfl import EventFlow
from evfl.repr_util import generate_flowchart_graph
import json

flow = EventFlow()
with open("Demo007_2.bfevfl", "rb") as f:
    flow.read(f.read())

json_obj = json.dumps(generate_flowchart_graph(flow), indent=4, default=lambda x: str(x))

with open("Demo007_2.json", "w") as out:
    out.write(json_obj)