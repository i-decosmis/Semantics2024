import csv
import json 
   
TEST_SET_PATH = 'dataset/dataset_after_sixth/from_test.json'   
SAVING_PATH = 'test_scripts/analyzing_results/results/groundtruth.csv'
def convert_in_groundtruth():
    with open(TEST_SET_PATH, 'r') as json_file:
        users_data_test = json.load(json_file)
    fields = ["user","item","score"]
    rows_groundtruth = []
    for user, info in users_data_test.items():
        for film, datas in info[1].items():
            if float(datas[0]) >= 3:
                rows_groundtruth.append([user, datas[1], "1"])
    with open(SAVING_PATH, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(fields)
        for row in rows_groundtruth:
            writer.writerow(row)
        
convert_in_groundtruth()
