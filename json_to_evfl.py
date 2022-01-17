#!/usr/bin/env python
from evfl import EventFlow, Flowchart, Event, ActionEvent, SwitchEvent, ForkEvent, JoinEvent, SubFlowEvent, Actor, Container
from evfl.common import ActorIdentifier, StringHolder
from evfl.entry_point import EntryPoint
from evfl.util import IdGenerator, RequiredIndex, make_values_to_index_map
from typing import List
import json

with open("event.json", "r") as in_file:
    json_read = json.load(in_file)

flow = EventFlow()
flow.name = "Name"
flow.flowchart = Flowchart()
flow.flowchart.name = "Flow"
flowchart = flow.flowchart

json_read = json_read

i: int = 0
fork_events: List[ForkEvent] = []
edge_num: List[int] = []
join_events: List[JoinEvent] = []
while i < len(json_read):
    # Initialize nodes and edges
    node = json_read[i]
    if node['type'] == 'edge':
        i += 1
        continue
    # edge = json_read[i+1]

    # Initialize events, actors and params
    event = Event()
    # processed_events = []

    actor = Actor()
    actor.identifier.name = node['data'].get('actor')
    actor.actions.append(StringHolder(node['data'].get('action', '<placeholder action>')))
    actor.queries.append(StringHolder(node['data'].get('query', '<placeholder action>')))

    params = Container()
    params.data = node['data'].get('params')
    
    if node['node_type'] == 'action':
        
        event.data = ActionEvent()
        event.data.actor.v = actor
        flowchart.actors.append(actor)
        event.data.actor_action.v = actor.actions[0]
        event.data.params = params

    elif node['node_type'] == 'switch':
        
        event.data = SwitchEvent()
        event.data.actor.v = actor
        flowchart.actors.append(actor)
        event.data.actor_query.v = actor.queries[0]
        event.data.params = params
        
        # event.data.cases[node['id']] = RequiredIndex(edge['target'])
        # if len(processed_events) > 1:
        #     event.data.cases[node['id']].v = processed_events[i // 2]

    elif node['node_type'] == 'fork':
        event.data = ForkEvent()
        fork_events.append([event.data, json_read[i+1]['target']])

    elif node['node_type'] == 'join':
        event.data = JoinEvent()
        join_events.append([event.data, json_read[i+1]['target']])

    elif node['node_type'] == 'sub_flow':
        event.data = SubFlowEvent()
        event.data.res_flowchart_name = node['data']['res_flowchart_name']
        event.data.entry_point_name = node['data']['entry_point_name']
        event.data.params = params
    
    elif node['node_type'] == 'entry':
        ep = EntryPoint(node['data']['name'])
        flowchart.entry_points.append(ep)
        i += 1
        continue

    flowchart.add_event(event, IdGenerator())
    event.name = node['data']['name']
    i += 1
    
idx_map = make_values_to_index_map(flowchart.events)

# for event in flowchart.events:
for event, idx in idx_map.items():
    for fork in fork_events:
        ev = RequiredIndex()
        ev.v = event
        if fork[1] == idx:
            fork[0].forks.append(ev)
            fork[0].join.v = event
    for join in join_events:
        if join[1] == idx:
            join[0].nxt.v = event

with open("test.bfevfl", "wb") as f_mod:
    flow.write(f_mod)