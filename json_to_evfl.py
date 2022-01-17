#!/usr/bin/env python
from evfl import EventFlow, Flowchart, Event, ActionEvent, SwitchEvent, ForkEvent, JoinEvent, SubFlowEvent, Actor, Container
from evfl.common import ActorIdentifier, StringHolder
from evfl.util import IdGenerator, RequiredIndex
from evfl.repr_util import generate_flowchart_graph
import json

# flow = EventFlow()
# with open("Demo007_2.bfevfl", "rb") as f:
#     flow.read(f.read())

# json_obj = json.dumps(generate_flowchart_graph(flow), indent=4, default=lambda x: str(x))

# with open("event.json", "w") as out:
#     out.write(json_obj)

with open("event.json", "r") as in_file:
    json_read = json.load(in_file)

flow = EventFlow()
flow.name = "Name"
flow.flowchart = Flowchart()
flow.flowchart.name = "Flow"
flowchart = flow.flowchart
# flowchart = Flowchart()

json_read = json_read


i = 0
while i < len(json_read):
    node = json_read[i]
    edge = json_read[i+1]
    event = Event()
    if node['node_type'] == 'action':
        event.data = ActionEvent()


# for i in json_read:
#     event = Event()
#     if i['type'] == 'node':
#         if i['node_type'] == 'action':
#             event.data = ActionEvent()
#             actor = Actor()
#             actor.identifier.name = i['data']['actor']
#             actor.actions.append(StringHolder(i['data']['action']))

#             flowchart.actors.append(actor)

#             event.data.actor.v = actor

#             event.data.actor_action.v = actor.actions[0]

#             event.data.params = Container()
#             event.data.params.data = i['data']['params'] if i['data']['params'] else None
#         elif i['node_type'] == 'switch':
#             event.data = SwitchEvent()
#             actor = Actor()
#             actor.identifier.name = i['data']['actor']
#             actor.queries.append(StringHolder(i['data']['query']))
#             flowchart.actors.append(actor)
#             event.data.actor.v = actor
#             event.data.actor_query.v = actor.queries[0]
#             event.data.params = Container()
#             event.data.params.data = i['data']['params'] if i['data']['params'] else None
#             edge = next(json_read)
#             target = RequiredIndex(edge['target'])
#             event.data.cases[i['id']] = target
#             event.data.cases[i['id']].v = event # Needs to be the next event. Just sets the current event for now
#         elif i['node_type'] == 'fork':
#             continue
#             # event.data = ForkEvent()
#         elif i['node_type'] == 'join':
#             continue
#             # event.data = JoinEvent()
#         elif i['node_type'] == 'sub_flow':
#             event.data = SubFlowEvent()
#             event.data.res_flowchart_name = i['data']['res_flowchart_name']
#             event.data.entry_point_name = i['data']['entry_point_name']
#             event.data.params = Container()
#             event.data.params.data = i['data']['params'] if i['data']['params'] else None
#         elif i['node_type'] == 'entry':
#             continue
#         flowchart.add_event(event, IdGenerator())
#         event.name = i['data']['name']
#     elif i['type'] == 'edge':
#         pass
    

# new_flow.flowchart = flowchart
# new_flow.flowchart.name = "name"
with open("test.bfevfl", "wb") as f_mod:
    flow.write(f_mod)