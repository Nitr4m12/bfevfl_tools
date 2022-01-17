#!/usr/bin/env python
from evfl import EventFlow, Flowchart, Event, ActionEvent, SwitchEvent, ForkEvent, JoinEvent, SubFlowEvent, Actor, Container
from evfl.common import ActorIdentifier, StringHolder
from evfl.util import IdGenerator, RequiredIndex
import json

with open("event.json", "r") as in_file:
    json_read = json.load(in_file)

flow = EventFlow()
flow.name = "Name"
flow.flowchart = Flowchart()
flow.flowchart.name = "Flow"
flowchart = flow.flowchart

json_read = json_read

i = 0
while i < len(json_read):
    # Initialize nodes and edges
    node = json_read[i]
    edge = json_read[i+1]

    # Initialize events, actors and params
    event = Event()

    actor = Actor()
    actor.identifier.name = node['data']['actor'] if node['data']['actor'] else None
    actor.actions.append(StringHolder(node['data']['action']) if node['data']['action'] else None)
    actor.queries.append(StringHolder(node['data']['query']) if node['data']['query'] else None)

    params = Container()
    params.data = i['data']['params'] if i['data']['params'] else None

    flowchart.add_event(node, IdGenerator())
    event.name = node['data']['name']
    if node['node_type'] == 'action':
        event.data = ActionEvent()
        event.data.actor = actor
        flowchart.actors.v.append(actor)
        event.data.actor_action.v = actor.actions[0]
        event.data.params = params

    elif node['node_type'] == 'switch':
        event.data = SwitchEvent()
        event.data.actor = actor
        flowchart.actors.v.append(actor)
        event.data.params = params
        # TODO: connect edges

    elif node['node_type'] == 'fork':
        continue

    elif node['node_type'] == 'join':
        continue

    elif node['node_type'] == 'sub_flow':
        event.data = SubFlowEvent()
        event.data.res_flowchart_name = node['data']['res_flowchart_name']
        event.data.entry_point_name = node['data']['entry_point_name']
        event.data.params = params

    i += 2
    
with open("test.bfevfl", "wb") as f_mod:
    flow.write(f_mod)