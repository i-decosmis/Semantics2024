# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

from typing import List, Optional

import random
import fire
import json
import datetime
import re
from rapidfuzz import fuzz

from llama import Llama, Dialog
import os
import torch
# ONLY FOR WINDOWS ==========>
os.environ['PL_TORCH_DISTRIBUTED_BACKEND'] = 'gloo'
os.environ['NCCL_DEBUG'] = 'INFO'
torch.distributed.init_process_group(backend="gloo")
# ONLY FOR WINDOWS ==========>movies

INTRO_STRING_GENRES = "These are my favourite movie genres: ["
INTRO_STRING_FILMS = "These are my favourite movie(IN THIS LIST THE ORDER OF THE MOVIES DOES NOT REPRESENT ANY PREFERENCE): ["
END_STRING = "Sort this list using my preferences and suggest me only the first 10(In this list the order of the movies is random,In this list the order of the movie does not represent any preference) : ["
# SYSTEM_PROMPT = "Only recommend films released between 1919 and 2000. Write only the name and the year of the movies. Write a single list of movies."
SYSTEM_PROMPT = "You are a movie recommendere system. You will receive a list of movies or list of genres. You will generate a list of 50 movies based on the list of movies or genres in input. Write a single list of movies that comprends every genres in my preferences. Do not write anything else except the movie list."
history = [[]]
def main(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0.6,
    top_p: float = 0.9,
    max_seq_len: int = 4096,
    max_batch_size: int = 8,
    max_gen_len: Optional[int] = None,
):
    
    with open('dataset/dataset_before_sixth/from_train.json', 'r') as json_file:
        users_data = json.load(json_file)
    with open('dataset/dataset_before_sixth/from_test.json', 'r') as json_file:
        users_data_test = json.load(json_file)
    test_type = "4"
    test_properties = "4"
    test_type, test_properties, selected_user = get_tests(test_type, test_properties, users_data)
    if test_type == 3:
        print("Exit...")
    else:
        i = int(input("1)Test with genres\n2)Test with movie list\n3)Test with model recommended genres"))
        generator = Llama.build(
            ckpt_dir=ckpt_dir,
            tokenizer_path=tokenizer_path,
            max_seq_len=max_seq_len,
            max_batch_size=max_batch_size,
            )
        if i==1:
            test_type = 1
            test_properties = 1
        elif i==2:
            test_type = 2
            test_properties = 1
        elif i==3:
            test_type = 2
            test_properties = 2
        keys = list(users_data.keys())
        dialogs: List[Dialog] = make_dialog(test_type, test_properties, users_data[keys[int(selected_user)]], users_data_test[keys[int(selected_user)]])
        print(dialogs)
        #Inserire qui il generator
        results = generator.chat_completion(
            dialogs,
            max_gen_len=max_gen_len,
            temperature=temperature,
            top_p=top_p,
        )
        for dialog, result in zip(dialogs, results):
            timestamp = datetime.datetime.now()
            name_file = timestamp.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
            with open(name_file, 'w') as file:
                for msg in dialog:
                    file.write(f"{msg['role']}: {msg['content']}\n")
                    if i == 3:
                        history[-1].append({"role" : msg['role'], "content" : msg['content']})
                file.write(
                    f"> {result['generation']['role']}: {result['generation']['content']}"
                )
                if i == 3:
                    history[-1].append(
                    {"role": result['generation']['role'], "content": result['generation']['content']})
                file.write("\n==================================\n")
            if i!=3:  
                count = count_films(name_file, "dataset\movies.dat")
                with open(name_file, 'a') as file:
                    file.write(f"The number of movies guessed in the dataset is {count}/50")
            else:
                history[-1].append({"role": "user", "content": "Write a list of 50 movies based on the genres that you suggested"})
                print(history)
                dialogs: List[Dialog] = history
                results = generator.chat_completion(
                dialogs,
                max_gen_len=max_gen_len,
                temperature=temperature,
                top_p=top_p,
                )
                for dialog, result in zip(dialogs, results):
                    with open(name_file, 'w') as file:
                        for msg in dialog:
                            file.write(f"{msg['role']}: {msg['content']}\n")
                        file.write(
                            f"> {result['generation']['role']}: {result['generation']['content']}"
                        )
                        file.write("\n==================================\n")
                    count = count_films(name_file, "dataset\movies.dat")
                    with open(name_file, 'a') as file:
                        file.write(f"The number of movies guessed in the dataset is {count}/50")
            
def count_films(file_name, movie_file_name):
    with open(file_name, 'r') as file:
        model_answer = file.read()    
        lista1 = re.findall(r'\d+\.\s(.*?)(?:\s\(.*?\))?$', model_answer, re.MULTILINE)
    
    with open(movie_file_name, 'r') as file:
        movies_from_file = file.read()   
        lista2 = re.findall(r'::(.*?)\s\(\d{4}\)::', movies_from_file)

    lista1 = [s.lower() for s in lista1]
    lista2 = [s.lower() for s in lista2]

    theshold = 95
    count = 0

    for s2 in lista2:
        if any(fuzz.ratio(s1, s2) > theshold for s1 in lista1):
                count += 1

    return count

def get_tests(test_type, test_properties, users_data):
    '''while(test_type != "1" and test_type != "2" and test_type != "3"):
        test_type = input("Select an option:\n1)Test with genres(1)\n2)Test with favourite movie(2)\nExit(3)\n")
        if (test_type != "1" and test_type != "2" and test_type != "3"):
            print("Wrong answer, please try again")
    if test_type == "3":
        return 3,3,3,3

    while(test_properties != "1" and test_properties != "2" and test_properties != "3"):
        test_properties = input("Select an option:\n1)Test with system prompt(1)\n2)Test without system prompt(2)\nExit(3)\n")
        if (test_properties != "1" and test_properties != "2" and test_properties != "3"):
            print("Wrong answer, please try again")
    if test_properties == "3":
        return 3,3,3,3'''
        
    answer = "no"
    selected_user = -1
    while (answer == "no"):
        selected_user = input("There are {} users avaibles, select one using an index (0 - {})\n".format(len(users_data), len(users_data)-1))
        if int(selected_user) < 0 or int(selected_user) > len(users_data)-1:
            print("Wrong answer, please try again")
        else:
            print_user(users_data, selected_user)
            answer = input("Do you want to select this user? (yes/no)")
            if (answer != "yes" and answer != "no"):
                print("Wrong answer, please try again")
    
    return 0, 0, (selected_user)

def print_user(users_data, selected_user):
    print("This is the selected user:")
    keys = list(users_data.keys())
    print("Favourite genres:")
    for g in users_data[keys[int(selected_user)]][0]:
        print("    "+g)
    print("\nMovies:")
    for key, rate in users_data[keys[int(selected_user)]][1].items():
        print(f'    Name: {key}, Rate: {rate}')

def make_dialog(test_type, test_properties, user, test_user):
    if test_type == 1:
        if test_properties == 1:
            dialogs: List[Dialog] = make_dialog_one_one(user, test_user)
            return dialogs
        else:
            dialogs: List[Dialog] = make_dialog_one_two(user, test_user)
            return dialogs
    else:
        if test_properties == 1:
            dialogs: List[Dialog] = make_dialog_two_one(user, test_user)
            return dialogs
        else:
            dialogs: List[Dialog] = make_dialog_two_two(user, test_user)
            return dialogs

        
def make_dialog_one_one(user, test_user):
    genres_list = user[0]
    random.shuffle(genres_list)
    genres = "; ".join(genres_list)
    test_films_list = [film for film, rate in user[1].items() if rate in {"1.0", "2.0", "3.0","4.0" ,"5.0"}]
    random.shuffle(test_films_list)
    test_films ="; ".join(test_films_list)
    dialogs: List[Dialog] = [[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": INTRO_STRING_GENRES + genres + "]."}
    ]]
    return dialogs

def make_dialog_one_two(user, test_user):
    genres_list = user[0]
    random.shuffle(genres_list)
    genres = "; ".join(genres_list)
    test_films_list = [film for film, rate in user[1].items() if rate in {"1.0", "2.0", "3.0","4.0" ,"5.0"}]
    random.shuffle(test_films_list)
    test_films ="; ".join(test_films_list)
    dialogs: List[Dialog] = [[
        {"role": "user", "content":SYSTEM_PROMPT + INTRO_STRING_GENRES + genres +"]. "}
    ]]
    return dialogs

def make_dialog_two_one(user, test_user):
    selected_films = [film for film, rate in user[1].items() if rate in {"4.0","5.0"}]
    random.shuffle(selected_films)
    films = "; ".join(selected_films)
    test_films_list = [film for film, rate in user[1].items() if rate in {"1.0", "2.0", "3.0","4.0" ,"5.0"}]
    random.shuffle(test_films_list)
    test_films ="; ".join(test_films_list)
    dialogs: List[Dialog] = [[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": INTRO_STRING_FILMS + films + "]. Suggest me movies based on my favourite movies"}    
        ]]
    return dialogs

def make_dialog_two_two(user, test_user):
    selected_films = [film for film, rate in user[1].items() if rate in {"4.0","5.0"}]
    random.shuffle(selected_films)
    films = "; ".join(selected_films)
    test_films_list = [film for film, rate in user[1].items() if rate in {"1.0", "2.0", "3.0","4.0" ,"5.0"}]
    random.shuffle(test_films_list)
    test_films ="; ".join(test_films_list)
    '''history.append([{"role": "system", "content": "You are a movie recommendere system. You will receive a list of movies or list of genres. You will generate 3 movies gender based on the movies list in input."},
        {"role": "user", "content": INTRO_STRING_FILMS + films + "]. Tell me 3 genders that represent the movies inside the list."}])'''
    dialogs: List[Dialog] = [[
        {"role": "system", "content": "You are a movie recommendere system. You will receive a list of movies or list of genres. You will generate 3 movies gender based on the movies list in input."},
        {"role": "user", "content": INTRO_STRING_FILMS + films + "]. Tell me 3 genders that represent the movies inside the list."}    
        ]]
    return dialogs
        

if __name__ == "__main__":
    fire.Fire(main)
