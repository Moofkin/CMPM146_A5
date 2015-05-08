#planner
import json
from heapq import heappush, heappop
from collections import namedtuple
with open('crafting.json') as f:
   Crafting = json.load(f)
uniqueitems = []
uniqueActions = []
actions = {}

# this should build a dictionary of how many of each item you can have in total at any given point
totals = {}
for items in Crafting['Items']:
    totals[items] = 0
for action,rules in Crafting['Recipes'].items():
    if 'Requires' in rules:
        for each in rules["Requires"].keys():
            totals[each] = 1
    if 'Consumes' in rules:
        for each,amount in rules['Consumes'].items():
            if totals[each] < amount:
                totals[each] = amount
totals[u'wooden_axe'] = 0
totals[u'stone_axe'] = 0
totals[u'iron_axe'] = 0
totals[u'iron_pickaxe'] = 0
   
def make_checker(rules):
   consumes = []
   requires = []
   if 'Consumes' in rules:
      consumes = [(item,rules['Consumes'][item]) for item in rules['Consumes']]
   if 'Requires' in rules:
      requires = [item for item in rules['Requires'].keys()]
   produce = [(item,rules['Produces'][item]) for item in rules['Produces']]
   def check(state):
      checkflag = True
      for i,a in produce:
         if totals[i] == 0:
             checkflag = False
         if i in state:
            if state[i] >= totals[i]:
                checkflag = False
      for each in requires:
         if each not in state:
            checkflag = False
      for each,amount in consumes:
         if each not in state:
            checkflag = False
         else:
            if (state[each] < amount):
               checkflag = False
      return checkflag
   return check

def make_effect(rules):
   consumes = []
   if 'Consumes' in rules:
      consumes = [(item,rules['Consumes'][item]) for item in rules['Consumes']]
   produce = [(item,rules['Produces'][item]) for item in rules['Produces']]
   def effect(state):
      returnstate = state.copy()
      for i,a in consumes:
         returnstate[i] -= a
      for i,a in produce:
         if not i in state:
            returnstate[i] = 0
         returnstate[i] += a
      return returnstate
   return effect

def search(graph,initial,is_goal):
   for each, amount in Crafting['Goal'].items():
       totals[each] = amount
   print "Max I can aquire: ", totals
   path = []
   if is_goal(initial):
      print "I'm done"
      return
   else:
      inventory = initial
      adjlist = graph(inventory)
      lookat = []

      for actions in adjlist:
        heappush(lookat, (actions[2], actions, path))

      while len(lookat) > 0:
         current = lookat.pop(0)
         path1Copy = []
         for items in current[2]:
            path1Copy.append(items)
         if is_goal(current[1][1]):
            current[2].append((current[1][0], current[1][1]))
            print "Hey I found a Path."
            for items in current[2]:
                print items
            return
         adjlist = graph(current[1][1])
         path1Copy.append((current[1][0], current[1][1]))
         for actions in adjlist:
            heappush(lookat, (heuristic(actions[2], current[0]), actions, path1Copy))

      return
   
def make_graph(state):
   for r in all_recipes:
      if r.check(state):
         yield (r.name, r.effect(state), r.cost, state.copy())

def heuristic(actionWeight, pathWeight):
    return actionWeight + pathWeight - 4

def is_goal(state):
   for item, amount in Crafting['Goal'].items():
      if item in state:
         if state[item] < amount:
            return False
      else:
         return False
   return True

if __name__ == '__main__':
   Recipe = namedtuple('Recipe',['name','check','effect','cost'])
   all_recipes = []
   for name, rule in Crafting['Recipes'].items():
      checker = make_checker(rule)
      effector = make_effect(rule)
      recipe = Recipe(name, checker, effector, rule['Time'])
      all_recipes.append(recipe)

   search(make_graph,Crafting['Initial'],is_goal)
   