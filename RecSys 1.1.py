import csv
import json
from math import sqrt
from statistics import mean

# Читает файлы и выдаёт два значения: кортеж с фильмами и словарь с юзерами и их оценками
def fread(file):
    with open(file) as f:
        freader = csv.reader(f, delimiter=',', skipinitialspace=True)
        movie_list = tuple(next(freader)[1:])
        res = {row[0]: row[1:] for row in freader}
    return movie_list, res

# Создаёт файл json и записывает туда текст
def make_json(filename, text):
    with open(filename, 'w') as file:
        json.dump(text, file, indent=5)

# Рассчитывает среднее для списка, игнорируя -1 
def avg(arg):
    m = mean([i for i in arg if i > 0])
    return round(m, 3)

# Преобразует список в int
def to_int(ar):
    return [int(i) for i in ar] 

# Рассчитывает сходство для всех пользователей и возвращает словарь 
# со значениями метрики сходства для каждого пользователя
def affinity(d, us):
    user_sims = {}
    for cur_us in d:
        if  cur_us != us:
            sum_uv, sum_u, sum_v = 0, 0, 0
            u, v = d[us], d[cur_us]
            for i in range(len(u)):
                if u[i] > 0 and v[i] > 0:
                    sum_uv += u[i] * v[i]
                    sum_u += u[i] ** 2
                    sum_v += v[i] ** 2
            sim = sum_uv / (sqrt(sum_u * sum_v))
            user_sims[cur_us] = round(sim, 3)
    return user_sims

# Возвращает К наиболее похожих пользователей
def kNN(K, dat, our_us):
    aff = affinity(dat, our_us)
    sort_aff = sorted(aff.items(), key = lambda x: x[1], reverse = True)
    return dict(sort_aff[0:K])

# Рассчитывает оценку пользователя для конкретного фильма
def mark(all_users, our_user, sim_users, mov_num):
    numerator, denominator = 0, 0
    for usr, simvu in sim_users.items():
        usr_lst = all_users[usr]
        usr_mov_mark = usr_lst[mov_num]
        if (usr_mov_mark > 0):
            numerator += simvu * (usr_lst[mov_num] - avg(usr_lst))
            denominator += abs(simvu)
    rui = avg(all_users[our_user]) + numerator / denominator
    return round(rui, 3)

# Осуществляет расчёт оценок для всех фильмов выбранного пользователя 
def make_marks(data, our_user, smlr_usrs, movies):
    results = {}
    for i in range(len(data[our_user])):
        if data[our_user][i] == -1:
            results[movies[i]] = mark(data, our_user, smlr_usrs, i)       
    return results

# Выдаёт рекомендацию на основе информации о похожих пользователях и предполагаемых оценках
def make_recommendation(sim_usrs, marks, movies, c_days, c_places, days, places):
    marks_copy = dict(marks)
    for cur_movie in marks_copy:
        mov_index = movies.index(cur_movie)
        for cur_sim_usr in sim_usrs:
            if c_days[cur_sim_usr][mov_index] in days:
                marks_copy[cur_movie] *= 1.2
            if c_places[cur_sim_usr][mov_index] in places:
                marks_copy[cur_movie] *= 1.2
    best_mark = max(marks_copy.values())
    recommended_movie = [k for k in marks_copy if marks_copy[k] == best_mark][0]
    return {recommended_movie: marks[recommended_movie]}
            
movies, data = fread('data.csv')
c_day = fread('context_day.csv')[1]
c_place = fread('context_place.csv')[1]
data = {k: to_int(v) for k, v in data.items()}
input_us_num = input("User: ")
input_user = 'User ' + input_us_num 
similar_users = kNN(4, data, input_user)
marks = make_marks(data, input_user, similar_users, movies)
recommendation = make_recommendation(similar_users, marks, movies, c_day, c_place, ('Sat', 'Sun'), ('h',))
json_text = {"user": input_us_num, "1": marks, "2": recommendation}
make_json('RecSys_results.json', json_text)








