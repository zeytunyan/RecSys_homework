
'''
Начальная популяция: 1.2 жадный выбор, начиная со случайного груза
Отбор: 2.2 выбрать только 20% самых приспособленных особей
Скрещивание: 3.1 многоточечный с 3мя точками
Мутация: 4.3 добавление 1 случайной вещи 10% особей
Новая популяция: 5.1 замена не более 30% худших особей на потомков
'''

from random import randrange, sample, choice, shuffle


def greedy_individual():
    n = len(items)
    weight, volume = 0, 0.0
    individual = [0 for i in range(n)]
    cur_item_num = randrange(n)
    for item_num in range(n):
        cur_item_num = (cur_item_num + 1) % n
        cur_item = items[cur_item_num]
        bit = weight + cur_item[0] < max_weight and volume + cur_item[1] < max_volume
        if bit:
            individual[cur_item_num] = int(bit)
            weight = weight + cur_item[0]
            volume = round(volume + cur_item[1], 1)
    return individual

def make_population():
    return [greedy_individual() for i in range(population_size)]
    
def fitness(individual):
    sum([item[2] for bit_flag, item in zip(individual, items) if bit_flag])
    ind_weight, ind_volume, ind_price = 0, 0.0, 0
    for bit_flag, item in zip(individual, items):
        if bit_flag:
            ind_weight += item[0]
            ind_volume = round(ind_volume + item[1], 1)
            ind_price += item[2]
    if ind_weight > max_weight or ind_volume > max_volume:
        ind_price = 0
    return ind_price, ind_weight, ind_volume

def fitnesses_for_all_items(input_population):
    fitnesses = []
    for individ_num, individ in enumerate(input_population):
        fitnesses.append((individ_num, fitness(individ)[0]))
    fitnesses.sort(key = lambda i: i[1], reverse = True)
    return fitnesses

def selection(in_population, in_fitnesses):
    individs_number = round(len(in_population) * 0.2)
    best_individs = in_fitnesses[:individs_number]
    return [in_population[key] for key in dict(best_individs).keys()]

def crossingover(mother, father):
    points = sample(range(1, len(mother) - 1), 3)
    points.sort()
    first_child = mother[:points[0]] + father[points[0]:points[1]] + mother[points[1]:points[2]] + father[points[2]:]
    second_child = father[:points[0]] + mother[points[0]:points[1]] + father[points[1]:points[2]] + mother[points[2]:]
    return [first_child, second_child]
    
def children(parents):
    shuffle(parents)
    childs = []
    i = 0
    while i < len(parents) - 1:
        childs += crossingover(parents[i], parents[i + 1])
        i += 2
    return childs
    
def mutation(child_population):
    mutant_num = round(len(child_population) * 0.1)
    i = 0
    shuffle(child_population)
    while i < mutant_num:
        free_nums = []
        for free_num in range(len(child_population[i])):
            if not child_population[i][free_num]:
                free_nums.append(free_num)
        if len(free_nums):
            rand_free = choice(free_nums)
            child_population[i][rand_free] = 1
        else:
            mutant_num += 1
        i += 1

def new_population(old_population, new_individuals, old_fitnesses):
    replacements = int(len(old_population) * 0.3)
    old_fitnesses.sort(key = lambda i: i[1])
    shuffle(new_individuals)
    i = 0
    while i < replacements and i < len(new_individuals):
        old_num = old_fitnesses[i][0]
        old_population[old_num] = new_individuals[i]
        i += 1
    
with open('3.txt') as data:
    first_str = data.readline().split()
    max_weight = int(first_str[0])
    max_volume = float(first_str[1]);
    lines = data.readlines()
    
items = []
for line in lines:
    strings = line.split()
    items.append([int(strings[0]), float(strings[1]), int(strings[2])])

population_size = 200

population = make_population()
fitnesses = fitnesses_for_all_items(population)
best = [fitnesses[0][1], population[fitnesses[0][0]]]
low_percents = 0

for i in range(100):
    selected = selection(population, fitnesses)
    descendants = children(selected)
    mutation(descendants)
    new_population(population, descendants, fitnesses)
    fitnesses = fitnesses_for_all_items(population)
    low_percent = abs((best[0] - fitnesses[0][1]) / ((best[0] + fitnesses[0][1]) / 2)) < 0.1
    if low_percent:
        low_percents += 1
    best = [fitnesses[0][1], population[fitnesses[0][0]]]
    if low_percents > 30:
        break

best_fit = fitness(best[1])
print(best_fit)
with open("5.2 res.txt", 'w') as res:
    print("Список предметов: ", file = res)
    for result_item in range(len(best[1])):
        if best[1][result_item]:
            print(items[result_item], file = res)
    
    print(f'''
Оптимальный вес: {best_fit[1]}
Оптимальный объём: {best_fit[2]}
Ценность: {best_fit[0]}
''', file = res)
    

    