import json
import re
import os
import pandas as pd

how_many_per_user={}
at_number = 0 # 0 = no limit , 5 = @5, 10 = @10

RESULTS_JSON_MOVIES_PATH = 'test_scripts/analyzing_results/results/movies/results_movies.json'
RESULTS_JSON_GENRES_PATH = 'test_scripts/analyzing_results/results/genres/results_genres.json'
GROUNDTRUTH_PATH = 'test_scripts/analyzing_results/results/groundtruth.csv'
DATASET_TEST_PATH = 'dataset/dataset_after_sixth/from_test.json'
SAVE_PATH_MOVIES = 'test_scripts/analyzing_results/metrics/movies/how_many_per_user_movies.json'
SAVE_PATH_MOVIES_AT_FIVE = 'test_scripts/analyzing_results/metrics/movies/how_many_per_user_movies_at_five.json'
SAVE_PATH_MOVIES_AT_TEN = 'test_scripts/analyzing_results/metrics/movies/how_many_per_user_movies_at_ten.json'
SAVE_PATH_GENRES = 'test_scripts/analyzing_results/metrics/genres/how_many_per_user_genres.json'
SAVE_PATH_GENRES_AT_FIVE = 'test_scripts/analyzing_results/metrics/genres/how_many_per_user_genres_at_five.json'
SAVE_PATH_GENRES_AT_TEN = 'test_scripts/analyzing_results/metrics/genres/how_many_per_user_genres_at_ten.json'

def main():
# Change the results_genres or results_movies
    with open(RESULTS_JSON_GENRES_PATH, 'r') as f:
        data_results = json.load(f)
        
    ground_truth = pd.read_csv(GROUNDTRUTH_PATH)
    
    with open(DATASET_TEST_PATH, 'r') as json_file:
        users_data_test = json.load(json_file)
        
    new_data = {}
    
    for user_id, info in data_results.items():
        i = 0
        if info != "none":
            # Adding history to avoid duplicated favourites
            movie_founded = []
            for movie_number in info[2]:
                # Check if film already in favourites
                if not movie_number[0] in movie_founded:
                    movie_founded.append(movie_number[0])
                    # Stopping early if working @5 or @10
                    if at_number != 0:
                        if i >= at_number:
                            break
                    # Updating dictionary if movie_number is favourite of the given user
                    update_dictionary(int(user_id), movie_number[0],ground_truth)
                i += 1
            # If user exist in the dictionary after the search, add the number of film suggested or @5 or @10
            if str(user_id) in how_many_per_user:
                if at_number == 0:
                    how_many_per_user[str(user_id)] = [how_many_per_user[str(user_id)], info[1]]
                else:
                    how_many_per_user[str(user_id)] = [how_many_per_user[str(user_id)], at_number]
            # Else no key for the current user so creating key with 0 movies favourite and the total suggested or @5 or @10
            else:
                if at_number == 0:
                    how_many_per_user[str(user_id)] = [0, info[1]]
                else:
                    how_many_per_user[str(user_id)] = [0, at_number]
        else:
            how_many_per_user[str(user_id)] = [-1, 50]
            
        # Adding the number of favourite movies per user in the dictionary(for metrics)
        user_info = users_data_test[str(user_id)][1]
        count = 0
        for movies_info in user_info.values():
                if float(movies_info[0]) >= 3:
                    count += 1
        how_many_per_user[str(user_id)].append(count)
    # Saving json
    if at_number == 0:
        with open(SAVE_PATH_GENRES, "w") as file_json:
            json.dump(how_many_per_user, file_json)
    elif at_number == 5:
        with open(SAVE_PATH_GENRES_AT_FIVE, "w") as file_json:
            json.dump(how_many_per_user, file_json)
    else:
        with open(SAVE_PATH_GENRES_AT_TEN, "w") as file_json:
            json.dump(how_many_per_user, file_json)
            

def update_dictionary(selected_user, number, ground_truth):
    user_prediction = ground_truth[ground_truth['user'] == selected_user]
    for _, row in user_prediction.iterrows():
        if int(number) != -1:
            if row['user'] > selected_user:
                break
            if int(row['user']) == int(selected_user) and int(row['item']) == int(number):
                how_many_per_user[str(selected_user)] = how_many_per_user.get(str(selected_user), 0) + 1
                break
        
    
if __name__ == "__main__":
    main()