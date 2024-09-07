import json
import statistics

HOW_MANY_USER_MOVIES_PATH = 'test_scripts/analyzing_results/metrics/movies/how_many_per_user_movies.json'
HOW_MANY_USER_MOVIES_PATH_FIVE = 'test_scripts/analyzing_results/metrics/movies/how_many_per_user_movies_at_five.json'
HOW_MANY_USER_MOVIES_PATH_TEN = 'test_scripts/analyzing_results/metrics/movies/how_many_per_user_movies_at_ten.json'

HOW_MANY_USER_GENRES_PATH = 'test_scripts/analyzing_results/metrics/genres/how_many_per_user_genres.json'
HOW_MANY_USER_GENRES_PATH_FIVE = 'test_scripts/analyzing_results/metrics/genres/how_many_per_user_genres_at_five.json'
HOW_MANY_USER_GENRES_PATH_TEN = 'test_scripts/analyzing_results/metrics/genres/how_many_per_user_genres_at_ten.json'

with open(HOW_MANY_USER_GENRES_PATH, "r") as file_json:
    how_many_per_user = json.load(file_json)
            
with open(HOW_MANY_USER_GENRES_PATH_FIVE, "r") as file_json:
    how_many_per_user_at_five = json.load(file_json)
            
with open(HOW_MANY_USER_GENRES_PATH_TEN, "r") as file_json:
    how_many_per_user_at_ten = json.load(file_json)
    

def compute_global_precision(at_number):
    numerator = 0
    denominator = 0
    if at_number == 0:
        for key, data in how_many_per_user.items():
            numerator += data[0]
            denominator += data[1]
    elif at_number == 5:
        for key, data in how_many_per_user_at_five.items():
            numerator += data[0]
            denominator += data[1]
    elif at_number == 10:
        for key, data in how_many_per_user_at_ten.items():
            numerator += data[0]
            denominator += data[1]
    return numerator/denominator

def compute_global_recall(at_number):
    numerator = 0
    denominator = 0
    if at_number == 0:
        for key, data in how_many_per_user.items():
            numerator += data[0]
            denominator += data[2]
    elif at_number == 5:
        for key, data in how_many_per_user_at_five.items():
            numerator += data[0]
            denominator += data[2]
    elif at_number == 10:
        for key, data in how_many_per_user_at_ten.items():
            numerator += data[0]
            denominator += data[2]
    return numerator/denominator

def compute_f1_score(precision, recall):
    return 2 * (precision * recall) / (precision + recall)
            
precision_per_user = {}
precision_per_user_at_five = {}
precision_per_user_at_ten = {}

recall_per_user = {}
recall_per_user_at_five = {}
recall_per_user_at_ten = {}

for user, data in how_many_per_user.items():
    if data[0] > 0:
        precision_per_user[user] = 1
        precision_per_user[user] = data[0]/data[1]
        recall_per_user[user] = 1
        recall_per_user[user] = data[0]/data[2]
    else:
        precision_per_user[user] = 0
        recall_per_user[user] = 0

for user, data in how_many_per_user_at_five.items():
    if data[0] > 0:
        precision_per_user_at_five[user] = 1
        precision_per_user_at_five[user] = data[0]/data[1]
        recall_per_user_at_five[user] = 1
        recall_per_user_at_five[user] = data[0]/data[2]
    else:
        precision_per_user_at_five[user] = 0
        recall_per_user_at_five[user] = 0
        
for user, data in how_many_per_user_at_ten.items():
    if data[0] > 0:
        precision_per_user_at_ten[user] = 1
        precision_per_user_at_ten[user] = data[0]/data[1]
        recall_per_user_at_ten[user] = 1
        recall_per_user_at_ten[user] = data[0]/data[2]
    else:
        precision_per_user_at_ten[user] = 0
        recall_per_user_at_ten[user] = 0
       
global_precision = compute_global_precision(0)
global_precision_at_five = compute_global_precision(5)
global_precision_at_ten = compute_global_precision(10)

global_recall = compute_global_recall(0)
global_recall_at_five = compute_global_recall(5)
global_recall_at_ten = compute_global_recall(10)

f1_score = compute_f1_score(global_precision, global_recall)
f1_score_at_five = compute_f1_score(global_precision_at_five, global_recall_at_five)
f1_score_at_ten = compute_f1_score(global_precision_at_ten, global_recall_at_ten)

print("global_precision: " + str(global_precision))
print("global_precision_at_five: " + str(global_precision_at_five))
print("global_precision_at_ten: " + str(global_precision_at_ten))
print("---------------------------------------------------")
print("global_recall: " + str(global_recall))
print("global_recall_at_five: " + str(global_recall_at_five))
print("global_recall_at_ten: " + str(global_recall_at_ten))
print("---------------------------------------------------")
print("f1_score: " + str(f1_score))
print("f1_score_at_five: " + str(f1_score_at_five))
print("f1_score_at_ten: " + str(f1_score_at_ten))



