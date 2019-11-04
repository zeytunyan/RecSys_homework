from surprise import Dataset
from surprise import KNNWithMeans
from surprise import get_dataset_dir

# Возвращает словарь с номерами фильмов и высчитанными оценками
def get_top_n(predictions, n):
    top_n = [[iid, round(est, 3)] for uid, iid, t_r, est, _ in predictions]
    top_n.sort(key=lambda x: x[1], reverse=True)
    return top_n[:n]

# Забирает данные из файла u.item и возвращает их в виде списка
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
