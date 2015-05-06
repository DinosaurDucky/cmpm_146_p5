from collections import namedtuple
from heapq import heappush, heappop
import json
import timeit



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

     

      #getting current state should be working
      current_dist, current_state = heappop(Q)
      current_hash = inventory_to_tuple(current_state)


    


      #reached goal should be working
      if is_goal(current_state):
       
         total_cost = dist[current_hash]         
         while current_state:
            plan.append(current_state)
            current_state = parent[  inventory_to_tuple(current_state)   ]
         plan.reverse()
         return total_cost, plan



      if dist[current_hash] > limit:
         break;
      else:


        
         neighbors = graph(current_state)

         for neighbor in neighbors:
           
            
            inven = neighbor[1]

            weight = neighbor[2]
            name = inventory_to_tuple(inven)

            alternate = dist[current_hash] + weight


            if name not in dist or alternate < dist[name]:
              
           
               dist[name] = alternate

               parent[name] = current_state
               if name not in Q and dist[name] < limit:
           
               
                  heappush(Q, (heuristic(inven), inven) )
        
   return ("not found", [])


















#should be working
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














#should be working
def make_effector(rule):
   # this code runs once
   # do something with rule['Produces'] and rule['Consumes']
   def effect(state):
      
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







#should be working
Recipe = namedtuple('Recipe',['name','check','effect','cost'])
all_recipes = []
for name, rule in Crafting['Recipes'].items():
   checker = make_checker(rule)
   effector = make_effector(rule)
   recipe = Recipe(name, checker, effector, rule['Time'])
   all_recipes.append(recipe)








#could working
def graph(state):
   tempList = []
  
   for r in all_recipes:
      
      if r.check(state):
         tempD = dict(state)
         tempList.append  ((r.name, dict(r.effect(tempD )), r.cost))

   return tempList


#add name of action




optimal = {"wooden_pickaxe": 18, 'stone_pickaxe':31, 'furnace': 48, "iron_pickaxe":83, "bench":6, "wood":4 }

requiredItems = {}
for req in Crafting['Recipes'].items():
   if 'Requires' in req[1]:
      for reqI in req[1]['Requires']:
         requiredItems[reqI] =1


consumedItems = {}
for req in Crafting['Recipes'].items():
   if 'Consumes' in req[1]:
      for reqI in req[1]['Consumes']:
         consumedItems[reqI] =  req[1]['Consumes'][reqI]


maxConsumables = {
   "coal"   : 1, 
   "cobble" : 8, 
   "ingot"  : 6, 
   "ore"    : 1, 
   "plank"  : 4, 
   "rail"   : Crafting['Goal']['rail']  if 'rail' in Crafting['Goal'] else 0, 
   "stick"  : 2, 
   "wood"   : 1,  
}


#might be working
def heuristic(state):
   dist = 0
   for item, count in state.items():
      if count > 1 and item not in Crafting['Goal'] and item in requiredItems:
#         print "here"
         return float('inf')
      elif item in Crafting['Goal'] and count > Crafting['Goal'][item]:
#         print "there"
         return float('inf')
      #elif item in maxConsumables and count > maxConsumables[item]:
         #print count, " is too many of ", item
         #return float('inf')



      """
      elif item in consumedItems and count > consumedItems[item]:
         print "everywhere", consumedItems[item]
         return float('inf')
      """





   #now we have a trimmed goal, showing what we need, and an inventory with "extra items"

   for item in state:
      if item in Crafting['Goal']:
         dist +=     max((Crafting['Goal'][item] - state[item]),0)
      else:
         dist += state[item]

   return dist

   """
   
   #attempt 1


   glist = [] #dict(Crafting['Goal'])
   ilist = []

   for goal in Crafting['Goal']:
      glist.append( (goal, Crafting['Goal'][goal]) )

   for item in state:
      ilist.append( (item, state[item]) )

   while glist:
      goal,numG = glist.pop();
      found = False;

      #go through inventory
      for tupleT in ilist:

         item, numI = tupleT

         #if the inventory has our goal item
         if item == goal:
            #figure out if we made too many or need to make more
            #how many we need minus how many we have
            dif = numG - numI

            #if we are missing some
            if dif>0 :
               ilist.remove(tupleT)
               d

            #too many
            elif dif<0:
               print

            #just right
            else: 

            found = True;
            break;

      for item in ilist:
         dist += ilist[item]



   """
   """


      #attemp 2

      for goal in glist:
         for item in ilist:
            if item == goal:

               if ilist[item] > glist[item]:
                  #leaves the extra
                  ilist[item] -= glist[item]
                  del glist[item]
               
               elif ilist[item] < glist[item]:
                  #shows how many are left
                  glist[item] -= ilist[item]
                  del ilist[item]
               4
               else: # ilist[item] == glist[item]
                  del glist[goal]
                  del ilist[goal]

      











      #attemp 3
      h = 0


      for item in Crafting['Goal']:
    
         if item in optimal:
            if item not in state:
               h += optimal[item] * Crafting['Goal'][item]
            else:
               h += optimal[item] * (Crafting['Goal'][item]-state[item])

         else:
            if item not in state:
               h += Crafting['Goal'][item]

            else:
               h += Crafting['Goal'][item] - state[item]






      print"h is", h
      return h
      """








#should be working
def is_goal(state):
   for item in Crafting['Goal']:
      if item not in state or state[item] < Crafting['Goal'][item] :
         return False
   return True









limit = 275
initial_state = Crafting['Initial']

cost, steps = search(graph, initial_state, is_goal, limit, heuristic)

count = 1
for step in steps:
   print "step ", count, ": ", step
   count += 1
print "cost: ", cost




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

