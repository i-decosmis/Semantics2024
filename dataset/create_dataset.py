import sys
import csv
import re
import json

# Path of the file movie
PATH_MOVIE = "movies.dat"
# Dictionary where all the films with their relase year and genre will be saved
film_dictionary = {}

# Creating the film Dictionary with all the data, the key of the dictionary is the film id, the items
# are the title, the year and the genres of the film splitted with "|"
def create_film_dictionary():
    input_movies = open('movies.dat', 'r')
    for row in input_movies:    
        columns = row.rstrip('\n').split('::')
        film_id = columns[0]
        film_name = columns[1]
        match = re.match(r"(.*?)\s*\((\d+)\)", film_name)
        title, year = match.groups()
        film_genres = columns[2]
        film_dictionary[film_id]=[title, year, film_genres, film_id]
    input_movies.close()

# Creating the json file of the users of the input dataset
def create_json(path_up):
    current_user = 1
    users_preferences = {}

    current_user_info = []
    current_user_genres = {}
    current_user_films = {}

    rows = []
    # Reading the csv file
    with open(path_up, 'r') as file:
        csvreader = csv.reader(file)
        header = next(csvreader)
        # Cicling for each row in the file
        for row in csvreader:
            # If the user is the current user keep saving his data in the relative dictionaries
            # Adding the genre of the film into the current_user_genres dictionary
            if int(row[0]) == current_user:
                #current_user_films[film_dictionary[row[1]][0]] = row[2] for train case
                current_user_films[film_dictionary[row[1]][0]] = [row[2],film_dictionary[row[1]][3]]
                add_film_genre(row, film_dictionary, current_user_genres)
            # If the user has changed, ordering the genres dictionary in decreasing order and insert the most 2
            # watched genres into the first position of the current_user_info
            # Ordering all the watched film based of the rating
            # Adding the user info into the users_preferences dictionary using as key the current user id and as item
            # the dictionary of his info
            # After that the list and the dictionaries used for the current user are reset and
            # the new user is examined
            if int(row[0]) != current_user:
                current_user_genres = dict(sorted(current_user_genres.items(), key=lambda item: item[1], reverse=True))
                #current_user_films = dict(sorted(current_user_films.items(), key=lambda item: item[1], reverse=True))
                current_user_info.append(list(current_user_genres.keys())[:2])
                current_user_info.append(current_user_films)
                users_preferences[current_user]=current_user_info
                current_user = int(row[0])
                current_user_info = []
                current_user_genres = {}
                current_user_films = {}
                #current_user_films[film_dictionary[row[1]][0]] = row[2]
                current_user_films[film_dictionary[row[1]][0]] = [row[2],film_dictionary[row[1]][3]]
                add_film_genre(row, film_dictionary, current_user_genres)

        current_user_genres = dict(sorted(current_user_genres.items(), key=lambda item: item[1], reverse=True)) 
        #current_user_films = dict(sorted(current_user_films.items(), key=lambda item: item[1], reverse=True)) 
        current_user_info.append(list(current_user_genres.keys())[:2])
        current_user_info.append(current_user_films)
        users_preferences[current_user]=current_user_info

        # After the last user is saved, the dictionary will be exported in a json file
    with open("from_" + re.search(r"/(\w+)_", path_up).group(1) + ".json", "w") as file:
        json.dump(users_preferences, file)

# In this function i just add into a dictionary the genres of the
# film the user has watched, if the genre is new in the dictionary
# the value will be 1, otherwise the value will be + 1
# The genre will be saved only if the user rated the film 4 or more
def add_film_genre(row, film_dictionary, current_user_genres):
    if int(float(row[2])) >= 4:
        genre_list = film_dictionary[row[1]][2].split('|')
        for i, genre in enumerate(genre_list):
            if genre in current_user_genres:
                current_user_genres[genre] += 1
            else:
                current_user_genres[genre] = 1
        
    

if __name__ == "__main__":
    create_film_dictionary()
    create_json("./test_ratings/ratings_frame.csv")