import json
import re
import os
from rapidfuzz import fuzz

MOVIE_DATASET_PATH = 'test_scripts/analyzing_results/movies.dat'
PATH_MODEL_RESPONSE_MOVIES = 'test_scripts/analyzing_results/results/movies/response_movies.json'
PATH_MODEL_RESPONSE_GENRES = 'test_scripts/analyzing_results/results/genres/response_genres.json'
REGULAR_EXPRESSION_MODEL_RESPONSE = r'\d+\.\s(.*?)(?:\s\(|\n|$)'
REGULAR_EXPRESSION_DATASET_MOVIES = r'(\d+)::(.*?)\s\(\d{4}\)::'
SAVING_PATH_MOVIES = 'test_scripts/analyzing_results/results/movies/results_movies.json'
SAVING_PATH_GENRES = 'test_scripts/analyzing_results/results/genres/results_genres.json'


def main():

    with open(PATH_MODEL_RESPONSE_GENRES, 'r') as f:
        data_response = json.load(f)

    new_data = {}

    for id, s in data_response.items():
        # Using regex to find movies
        titoli_film = re.findall(REGULAR_EXPRESSION_MODEL_RESPONSE, s)
        # If no movies found check if the string is a {} list and split
        if len(titoli_film) == 0:
            semicolon_count = s.count(";")
            comma_count = s.count(",")
            if semicolon_count > 0:
                s = s.strip("{}")
                titoli_film = s.split("; ")
            elif comma_count > 0:
                s = s.strip("{}")
                titoli_film = s.split(", ")
        
        # To lower case to better check similarity later
        titoli_film = [titolo.lower() for titolo in titoli_film]
        
        # Adding info into the new dictionary "user_id":"[movielist]"
        new_data[id] = titoli_film
    # Counting how many movies suggested are inside the dataset
    final_data = count_films(new_data)
    
    with open(SAVING_PATH_GENRES, "w") as file_json:
        json.dump(final_data, file_json)

# Organizing and extracting the date into a dictionary:
# "user_id": [number_of_movies_inside_the_dataset, number_of_movies_suggested, ratio(5->0)] | "none"
# The item associated to the "user_id" can be none if the model didn't suggest any movies
def count_films(user_list):
    final_data = {} 
    with open(MOVIE_DATASET_PATH, 'r') as file:
        movies_from_file = file.read()   
        movies_list_dataset = re.findall(REGULAR_EXPRESSION_DATASET_MOVIES, movies_from_file)

    movies_list_dataset = [(number, title.lower()) for number, title in movies_list_dataset]

    theshold = 95
    count = 0
    movies_list = []
    for key, movies in user_list.items():
        if len(movies) != 0:
            for i, title in enumerate(movies, start=1):
                found = False
                for number, film in movies_list_dataset:
                    if fuzz.ratio(film, title) > theshold:
                        count += 1
                        movies_list.append([number, 5-((5/len(movies))*i)])
                        found = True
                        break
                if not found:
                    movies_list.append([-1, 5-((5/len(movies))*i)])
            final_data[key] = [count,len(movies),movies_list]
            movies_list = []
        else:
            final_data[key] = "none"
        count = 0
    return final_data

if __name__ == "__main__":
    main()