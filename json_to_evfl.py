#!/usr/bin/env python
from typing import List, Optional
from sys import argv
from pathlib import Path
import json


from evfl import EventFlow, Flowchart, Event, ActionEvent, SwitchEvent, ForkEvent, JoinEvent, SubFlowEvent, Actor, Container
from evfl.common import ActorIdentifier, StringHolder
from evfl.entry_point import EntryPoint
from evfl.util import IdGenerator, RequiredIndex, make_values_to_index_map
from copy import deepcopy


with open(argv[1], "r") as in_file:
    json_read = json.load(in_file)

flow = EventFlow()
flow.name = Path(argv[1]).stem
flow.flowchart = Flowchart()
flow.flowchart.name = Path(argv[1]).stem
flowchart = flow.flowchart
global_stack = []
# json_read = json_read

def look_for_edge(src_node: dict, json_dict: dict):
    events: dict = deepcopy(json_dict)
    edges: list = []
    for node in events:
        if node['type'] == 'edge' and src_node['id'] == node['source']:
            edges.append(node)
    return edges

def look_for_next(edges: list, json_dict: dict):
    events: dict = deepcopy(json_dict)
    targets = []
    for node in events:
        if node['type'] == 'node' and any(node['id'] == edge['target'] for edge in edges):
            targets.append(node)
    return targets

def look_for_join(json_dict: dict):
    events: dict = deepcopy(json_dict)
    for node in events:
        if node['type'] == 'node' and node['node_type'] == 'join' and node not in global_stack:
            global_stack.append(node)
            return node

def look_for_actors(json_dict: dict):
    events: dict = deepcopy(json_dict)
    traversed_actors: List[str] = []
    traversed_actions: List[str] = []
    traversed_queries: List[str] = []
    for node in events:
        if node['type'] == 'node' and node['data'].get("actor") and node['data']['actor'] not in traversed_actors:
            actor = Actor()
            actor.identifier.name = node['data'].get('actor')
            actors_dict[node['data']['actor']] = {
                'actor': actor,
            }
            traversed_actors.append(node['data']['actor'])

    for node in events:
        if node['type'] == 'node' and node['data'].get('action') and node['data']['action'] not in traversed_actions:
            actors_dict[node['data']['actor']]['actor'].actions.append(StringHolder(node['data']['action']))
            traversed_actions.append(node['data']['action'])

        elif node['type'] == 'node' and node['data'].get('query') and node['data']['query'] not in traversed_queries:
            actors_dict[node['data']['actor']]['actor'].queries.append(StringHolder(node['data']['query']))
            traversed_queries.append(node['data']['query'])

def build_event(node: dict, edges: list, flowchart: Flowchart, targets: List[dict]):
    # Initialize events, actors and params
    event = Event()

    params = Container()
    params.data = node['data'].get('params')

    temp_edges = []
    temp_flowc = Flowchart()

    if node['data'].get('action'):
        for act in actors_dict[node['data']['actor']]['actor'].actions:
            if str(act) == node['data']['action']:
                action = act
    
    if node['data'].get('query'):
        for que in actors_dict[node['data']['actor']]['actor'].queries:
            if str(que) == node['data']['query']:
                query = que

    if node['node_type'] == 'action':
        
        event.data = ActionEvent()
        event.data.actor.v = actors_dict[node['data']['actor']]['actor']

        event.data.actor_action.v = action
        event.data.params = params

    elif node['node_type'] == 'switch':
        
        event.data = SwitchEvent()
        event.data.actor.v = actors_dict[node['data']['actor']]['actor']
        event.data.actor_query.v = query
        event.data.params = params

        if edges:
            for edge in edges:
                if not edge['data'].get('virtual'):
                    event.data.cases[edge['data']['value']] = RequiredIndex(edge['target'])
                else:
                    event.data.cases[len(edges) - 1] = RequiredIndex(edge['target'])
                    
    elif node['node_type'] == 'fork':
        event.data = ForkEvent()
        event.data.join._idx = [target['id'] for target in targets][0]
        if edges:
            for edge in edges:
                req_index = RequiredIndex(edge['target'])
                event.data.forks.append(req_index)

    elif node['node_type'] == 'join':
        event.data = JoinEvent()

    elif node['node_type'] == 'sub_flow':
        event.data = SubFlowEvent()
        event.data.res_flowchart_name = node['data']['res_flowchart_name']
        event.data.entry_point_name = node['data']['entry_point_name']
        event.data.params = params if params.data != None else None

    return event

def set_targets(flowchart: Flowchart, events: dict):
    for event in flowchart.events:
        if type(event.data) == ActionEvent:
            try:
                event.data.nxt.v = events[events[event.name]["target_names"][0]]['event']
            except:
                continue

        elif type(event.data) == SwitchEvent:
            if len(event.data.cases) != 0:
                for i in range(len(event.data.cases)):
                    event.data.cases[i].v = events_by_idx[event.data.cases[i]._idx]['event']

        elif type(event.data) == ForkEvent:
            for i in range(len(event.data.forks)):
                event.data.forks[i].v = events_by_idx[event.data.forks[i]._idx]['event']

            event.data.join.v = events_by_idx[event.data.join._idx]['event']

        elif type(event.data) == JoinEvent:
            event.data.nxt.v = events[events[event.name]["target_names"][0]]['event']

        elif type(event.data) == SubFlowEvent:
            try:
                event.data.nxt.v = events[events[event.name]["target_names"][0]]['event']
            except:
                continue


actors_dict = {}
look_for_actors(json_read)
for _, actor in actors_dict.items():
    flowchart.actors.append(actor['actor'])

events_dict = {}
events_by_idx = {}
for node in json_read:
    # Look for the current node's edge
    if node['type'] == 'edge':
        continue

    edges = look_for_edge(node, json_read)
    for edge in edges:
        assert edge['source'] == node['id']
    
    targets = look_for_next(edges, json_read)

    event: Event = build_event(node, edges, flowchart, targets)

    events_dict[node['data']['name']] = {
        "event": event,
        "name": node['data']['name'],
        "target_names": [target['data']['name'] for target in targets],
        "edges": edges
    }

    events_by_idx[node['id']] = {
        "event": event,
        "id": node['id'],
        "target_ids": [target['id'] for target in targets],
        "edges": edges
    }
    
    if node['node_type'] == 'entry':
        ep = EntryPoint(node['data']['name'])
        # ep.main_event.v = edges[0]['target']
        flowchart.entry_points.append(ep)
        continue

    flowchart.add_event(event, IdGenerator())
    event.name = node['data']['name']

for i in range(len(flowchart.entry_points)):
    flowchart.entry_points[i].main_event.v = events_dict[events_dict[flowchart.entry_points[i].name]['target_names'][0]]['event']
set_targets(flowchart, events_dict)
    
with open(argv[1].replace('.json', '.bfevfl'), "wb") as f_mod:
    flow.write(f_mod)
