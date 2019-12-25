from random import randrange, random, choice
from deap import algorithms, base, creator, tools
import numpy

def evalKnapsack(individual):
    weight = 0
    volume = 0.0
    value = 0
    for item in individual:
        weight += items[item][0]
        volume += items[item][1]
        value += items[item][2]
    if volume > MAX_VOLUME or weight > MAX_WEIGHT:
        return MAX_WEIGHT, MAX_VOLUME,  0           
    return weight, volume, value

def cxSet(ind1, ind2):
    temp = set(ind1)                
    ind1 &= ind2
    ind2 ^= temp                    
    return ind1, ind2

def mutSet(individual):
    if random() < 0.5:
        if len(individual) > 0:
            individual.remove(choice(sorted(tuple(individual))))
    else:
        individual.add(randrange(NBR_ITEMS))
    return individual,

with open('3.txt') as data:
    first_str = data.readline().split()
    MAX_WEIGHT = int(first_str[0])
    MAX_VOLUME = float(first_str[1])
    lines = data.readlines()

NBR_ITEMS = len(lines)

items = {}
for i in range(NBR_ITEMS):
    strings = lines[i].split()
    items[i] = (int(strings[0]), float(strings[1]), int(strings[2]))

NGEN = 500
MU = 200
LAMBDA = 40
CXPB = 0.8
MUTPB = 0.2

creator.create("Fitness", base.Fitness, weights=(-1.0,-1.0, 1.0))
creator.create("Individual", set, fitness=creator.Fitness)

toolbox = base.Toolbox()
toolbox.register("attr_item", randrange, NBR_ITEMS)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_item, NBR_ITEMS)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evalKnapsack)
toolbox.register("mate", cxSet)
toolbox.register("mutate", mutSet)
toolbox.register("select", tools.selNSGA2)
   
pop = toolbox.population(n=MU)
stats = tools.Statistics(lambda ind: ind.fitness.values)
stats.register("avg", numpy.mean, axis=0)
stats.register("max", numpy.max, axis=0)
algorithms.eaMuPlusLambda(pop, toolbox, MU, LAMBDA, CXPB, MUTPB, NGEN, stats)

          