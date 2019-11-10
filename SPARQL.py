from surprise import Dataset
from surprise import KNNWithMeans
from surprise import get_dataset_dir
from SPARQLWrapper import SPARQLWrapper, JSON
import requests
import pandas as pd

# Возвращает словарь с номерами фильмов и высчитанными оценками
def get_top_n(predictions, n):
    top_n = [[iid, round(est, 3)] for uid, iid, t_r, est, _ in predictions]
    top_n.sort(key=lambda x: x[1], reverse=True)
    return top_n[:n]

# Забирает даный из файла u.item и возвращает их в виде списка
def get_movies_dict_from_file():
    movies_dict = {}
    pth = get_dataset_dir() + 'ml-100k/ml-100k/u.item'
    with open(pth) as f:
        for line in f:
            ln_lst = line.split('|')
            movies_dict[ln_lst[0]] = (ln_lst[1], ln_lst[2])
    return movies_dict

# Записывает результаты в файл
def print_in_file(uID, lst, filename):
    with open(filename, 'w') as f:
        print("User " + uID, file=f)
        for row in lst:
            print(row, file=f)

data = Dataset.load_builtin()
trainset = data.build_full_trainset()

kNN = KNNWithMeans(4, 4, {'name': 'cosine', 'min_support': 5})
kNN.fit(trainset)
testset = trainset.build_anti_testset()

userID = input("User: ")
# Чтобы алгоритм работал быстрее, сразу уберём всех пользователей, кроме выбранного
testset = filter(lambda x: x[0] == userID, testset)

predictions = kNN.test(testset)
top_n = get_top_n(predictions, 5)
movies = get_movies_dict_from_file()

for elem in top_n:
    elem.insert(1, movies[elem[0]])

print_in_file(userID, top_n, 'RecSys_result.txt')

###############################################################################

# Вытаскивает название фильма из рекомендации 
def get_film_name(cur_flm):
    # Эти артикли почему-то стоят в названиях впереди, после запятой (Big Lebowski, The)
    # Из-за этого не получается найти фильм по названию 
    articles = [
            ", The (", 
            ", A (", 
            ", An (",
            ", Das (",
            ", Der (",
            ", Det (",
            ", Le (",
            ", La (",
            ", L' (",
            ", Il (",
            ", O (",
            ]
    
    # Еси такой артикль найден, то он возвращается на место
    for article in articles:
        pos = cur_flm.find(article)
        if pos != -1: 
            film_name = article[2:len(article) - 1] + cur_flm[:pos]
            return film_name
           
    pos = cur_flm.find(' (')
    film_name = cur_flm[:pos]
    return film_name

# Возвращает номера фильмов в wikidata
def get_wiki_ids(api_endpnt, top_films):
    film_lst = []
    
    params = {
    'action' : 'wbsearchentities',
    'format' : 'json',
    'language' : 'en',
    }
       
    for flm in top_films:
        params['search'] = get_film_name(flm[1][0])
        
        # Если поиск не удался, номер фильма просто не будет добавлен в список, и программа продолжит своё выполнение
        try:
            res = requests.get(api_endpnt, params = params)
            res_id = res.json()['search'][0]['id']
            film_lst.append('wd:' + res_id)
        except IndexError:
            pass
        
    return film_lst

# Выводит результаты в консоль и в файл
def print_wikidata_results(res_df):
    pd.set_option('display.max_columns', 7)
    pd.set_option('display.width', 300)
    
    if len(res_df.columns) > 0:
        print(res_df[[
                'film.value',
                'filmLabel.value',
                'date.value',
                'actress.value', 
                'actressLabel.value',
                'minPublDate.value']])
    else:
        print("No matching records found")
        
    with open("SPARQL Results.txt", 'w') as f:
        print("User " + userID, file=f)
        if len(res_df.columns) > 0:
            print(res_df[[
                    'film.value',
                    'filmLabel.value',
                    'date.value',
                    'actress.value', 
                    'actressLabel.value',
                    'minPublDate.value']], file = f)
        else:             
             print("No matching records found", file = f)

API_ENDPOINT = "https://www.wikidata.org/w/api.php"
ids = get_wiki_ids(API_ENDPOINT , top_n)
values = "VALUES ?film { " + " ".join(ids) + " }"

sparql = SPARQLWrapper("https://query.wikidata.org/sparql")

sparql_query = """
SELECT ?film ?filmLabel ?date ?actress ?actressLabel (MIN(?publDate) AS ?minPublDate)
WHERE
{ 
  BIND(wd:Q172241 AS ?film).
  ?film wdt:P161 ?actress;             
        wdt:P577 ?date.                

# ?actress wdt:P106/wdt:P279* wd:Q33999.
  ?actress wdt:P21 wd:Q6581072.        
  
  ?roles wdt:P161 ?actress;            
         wdt:P31/wdt:P279* wd:Q11424;  
         wdt:P577 ?publDate.           
         
  SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
}
GROUP BY ?film ?filmLabel ?date ?actress ?actressLabel
HAVING (?minPublDate = ?date)                            
ORDER BY ?actressLabel 
"""

sparql_query = sparql_query.replace("BIND(wd:Q172241 AS ?film).", values)
print(sparql_query)

sparql.setQuery(sparql_query)

sparql.setReturnFormat(JSON)
results = sparql.query().convert()

results_df = pd.io.json.json_normalize(results['results']['bindings'])
print_wikidata_results(results_df)

    
    
    