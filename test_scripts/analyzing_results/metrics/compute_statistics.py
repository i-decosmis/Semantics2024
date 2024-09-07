import json

# Calculate statistics based on the json in input
# "user_d":[number_of_favourite_movies_found, number_of_total_movies_recommended, total_favourites_movies]

LOADING_HOW_MANY_MOVIES_PATH = 'test_scripts/analyzing_results/metrics/movies/how_many_per_user_movies.json'
LOADING_HOW_MANY_GENRES_PATH = 'test_scripts/analyzing_results/metrics/genres/how_many_per_user_genres.json'

SAVING_MOVIES_STATS_PATH = 'test_scripts/analyzing_results/metrics/movies/statistics_movies.txt'
SAVING_GENRES_STATS_PATH = 'test_scripts/analyzing_results/metrics/genres/statistics_genres.txt'

with open(LOADING_HOW_MANY_GENRES_PATH, 'r') as f:
    data_how_many_per_user_movies = json.load(f)

def main():
    num_none = count_none()
    percentage_none = (num_none / len(data_how_many_per_user_movies)) * 100
    num_at_least_1 = count_at_least(1)
    num_at_least_5 = count_at_least(5)
    percentage_at_least_1 = (num_at_least_1 / len(data_how_many_per_user_movies)) * 100
    percentage_at_least_5 = (num_at_least_5 / len(data_how_many_per_user_movies)) * 100

    with open(SAVING_GENRES_STATS_PATH, 'w') as f:
        f.write(f"Number of user without a movie: {num_none}\n")
        f.write(f"Percentage of user without a movie: {percentage_none}%\n")
        f.write(f"Number of user with at least 1 movie favourite found: {num_at_least_1}\n")
        f.write(f"Percentage of user with at least 1 movie favourite found: {percentage_at_least_1}%\n")
        f.write(f"Number of user with at least 5 movies favourite found: {num_at_least_5}\n")
        f.write(f"Percentage of user with at least 5 movies favourite found: {percentage_at_least_5}%\n")
            
def count_none():
    count = 0
    for key, data in data_how_many_per_user_movies.items():
        if data[0] == -1:
            count += 1
    return count

def count_at_least(number):
    count = 0
    for key, data in data_how_many_per_user_movies.items():
        if data[0] >= number:
            count += 1
    return count

if __name__ == "__main__":
    main()