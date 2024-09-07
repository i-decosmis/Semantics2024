import json
import csv

def read_dataset():
    with open('dataset/from_test.json', 'r') as json_file:
        users_data_test = json.load(json_file)
    return users_data_test
    
def create_csv_file(users_data_test):
    with open('test_scripts/test_five/ground_truth/base_ground_truth.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        field = ["user", "item", "score"]
        writer.writerow(field)
        for key, value in users_data_test.items():
            for inner_key, inner_value in value[1].items():
                writer.writerow([key, inner_value[1], "1"])
                
user = read_dataset()
create_csv_file(user)