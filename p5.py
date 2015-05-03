from collections import namedtuple
from heapq import heappush, heappop
import json

with open('Crafting.json') as f:
   Crafting = json.load(f)

# List of items that can be in your inventory:
#print Crafting['Items']
# example: ['bench', 'cart', ..., 'wood', 'wooden_axe', 'wooden_pickaxe']

# List of items in your initial inventory with amounts:
#print Crafting['Initial']
# {'coal': 4, 'plank': 1}

# List of items needed to be in your inventory at the end of the plan:
# (okay to have more than this; some might be satisfied by initial inventory)
#print Crafting['Goal']
# {'stone_pickaxe': 2}

# Dict of crafting recipes (each is a dict):
#print Crafting['Recipes']['craft stone_pickaxe at bench']
# example:
# {	'Produces': {'stone_pickaxe': 1},
#	'Requires': {'bench': True},
#	'Consumes': {'cobble': 3, 'stick': 2},
#	'Time': 1
# }

def inventory_to_tuple(d):
   Items = Crafting['Items']
   return tuple(d.get(name,0) for i,name in enumerate(Items))

#h = inventory_to_tuple(state_dict) # --> (0,0,0,0,5,0,0,0)

def inventory_to_set(d):
   return frozenset(d.items())


""" A* """
def search(graph, initial, is_goal, limit, heuristic):
   hash_init = inventory_to_tuple(initial)
   parent = {hash_init: None}
   dist = {hash_init: 0}
   Q = [ (heuristic(initial), initial) ]
   plan = []

   while Q:

      current_dist, current_state = heappop(Q)
      current_hash = inventory_to_tuple(current_state)

      print current_state
      """ found it! """
      if is_goal(current_state):
         print "found it!"
         total_cost = dist[current_hash]
         while current_state:
            plan.append(current_state)
            current_state = parent[inventory_to_tuple(current_state)]
         plan.reverse()
         return total_cost, plan
      if dist[current_hash] < limit:
         neighbors = graph(current_state)
         for neighbor in neighbors:
            weight = neighbor[2]
            name = inventory_to_tuple(neighbor[1])
            alternate = dist[current_hash] + weight
            if name not in dist or alternate < dist[name]:
               dist[name] = alternate
               parent[name] = neighbor[1]
               if name not in Q and dist[name] < limit:
                  print "dist: ", dist[name], "limit: ", limit
               
                  heappush(Q, (heuristic(name), neighbor[1]) )
   return ("not found", [])

def make_initial_state(inventory):
   #state = inventory_to_tuple(inventory)
   return inventory


def make_checker(rule):
   # this code runs once
   # do something with rule['Consumes'] and rule['Requires']
   
   def check(state):
      # this code runs millions of times
      if 'Requires' in rule:
         for key in rule['Requires']:
            if key not in state:
               return False
      if 'Consumes' in rule:
         for key in rule['Consumes']:
            if key not in state or state[key] < rule['Consumes'][key]:
               return False

      return True # or False
      
   return check

def make_effector(rule):
   # this code runs once
   # do something with rule['Produces'] and rule['Consumes']
   def effect(state):
      
      
      # this code runs millions of times
      #      for item in rule['Consumes']
      next_state = state #dummy cod
      if 'Consumes' in rule:
         for key in rule['Consumes']:
            next_state[key] -= rule['Consumes'][key]
      if 'Produces' in rule:
         for key in rule['Produces']:
            if key in next_state:
               next_state[key] += rule['Produces'][key]
            else:
               next_state[key] = rule['Produces'][key]
      return next_state
      
   return effect


Recipe = namedtuple('Recipe',['name','check','effect','cost'])
all_recipes = []
for name, rule in Crafting['Recipes'].items():
   checker = make_checker(rule)
   effector = make_effector(rule)
   recipe = Recipe(name, checker, effector, rule['Time'])
   all_recipes.append(recipe)




def graph(state):
   for r in all_recipes:
      if r.check(state):
         yield (r.name, r.effect(state), r.cost)

def heuristic(state):
   return 0

def is_goal(state):
   for item in Crafting['Goal']:
      if item not in state or state[item] < 1:
         return False
   return True


limit = 100
initial_state = make_initial_state(Crafting['Initial'])

print search(graph, initial_state, is_goal, limit, heuristic)




""" test a* """

""" 
t_initial = 'a'
t_limit = 20

edges = {'a': {'b':1,'c':10}, 'b':{'c':1}}

def t_graph(state):
   for next_state, cost in edges[state].items():
#      print "next_state: ", next_state, "cost: ", cost
      yield ((state,next_state), next_state, cost)

def t_is_goal(state):
   return state == 'c'

   
def t_heuristic(state):
   return 0

print search(t_graph, t_initial, t_is_goal, t_limit, t_heuristic)
"""
