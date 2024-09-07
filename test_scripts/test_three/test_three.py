# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

from typing import List, Optional

import random
import fire
import json
import datetime

from llama import Llama, Dialog
import os
import torch
# ONLY FOR WINDOWS ==========>
os.environ['PL_TORCH_DISTRIBUTED_BACKEND'] = 'gloo'
os.environ['NCCL_DEBUG'] = 'INFO'
torch.distributed.init_process_group(backend="gloo")
# ONLY FOR WINDOWS ==========>

INTRO_STRING_GENRES = "These are my favourite film genres: ["
INTRO_STRING_FILMS = "These are my favourite film: ["
END_STRING = "Sort this list using my preferences and suggest me only the first 10(In this list the order of the films is random,In this list the order of the films does not represent any preference) : ["
# SYSTEM_PROMPT = "Only recommend films released between 1919 and 2000. Write only the name and the year of the movies. Write a single list of movies."
SYSTEM_PROMPT = "Write only the name and the year of the movies. Write a single list of movies that comprends every genres in my preferences."

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
        i = 0
        generator = Llama.build(
            ckpt_dir=ckpt_dir,
            tokenizer_path=tokenizer_path,
            max_seq_len=max_seq_len,
            max_batch_size=max_batch_size,
            )   
        while i<4:
            print("faccio " + str(i))
            if i == 0:
                test_type = 1
                test_properties = 1
            elif i==1:
                test_type = 1
                test_properties = 2
            elif i==2:
                test_type = 2
                test_properties = 1
            elif i==3:
                test_type = 2
                test_properties = 2
            keys = list(users_data.keys())
            dialogs: List[Dialog] = make_dialog(test_type, test_properties, users_data[keys[int(selected_user)]], users_data_test[keys[int(selected_user)]])
            #Inserire qui il generator
            results = generator.chat_completion(
                dialogs,
                max_gen_len=max_gen_len,
                temperature=temperature,
                top_p=top_p,
            )
            for dialog, result in zip(dialogs, results):
                '''for msg in dialog:
                    print(f"{msg['role'].capitalize()}: {msg['content']}\n")
                print(
                    f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
                )
                print("\n==================================\n")'''
                timestamp = datetime.datetime.now()
                name_file = timestamp.strftime('%Y-%m-%d_%H-%M-%S') + '.txt'
                with open(name_file, 'w') as file:
                    for msg in dialog:
                        file.write(f"{msg['role'].capitalize()}: {msg['content']}\n")
                    file.write(
                        f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
                    )
                    file.write("\n==================================\n")
            i += 1

def get_tests(test_type, test_properties, users_data):
    while(test_type != "1" and test_type != "2" and test_type != "3"):
        test_type = input("Select an option:\n1)Test with genres(1)\n2)Test with favourite film(2)\nExit(3)\n")
        if (test_type != "1" and test_type != "2" and test_type != "3"):
            print("Wrong answer, please try again")
    if test_type == "3":
        return 3,3,3,3

    while(test_properties != "1" and test_properties != "2" and test_properties != "3"):
        test_properties = input("Select an option:\n1)Test with system prompt(1)\n2)Test without system prompt(2)\nExit(3)\n")
        if (test_properties != "1" and test_properties != "2" and test_properties != "3"):
            print("Wrong answer, please try again")
    if test_properties == "3":
        return 3,3,3,3
        
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
    
    return int(test_type), int(test_properties), (selected_user)

def print_user(users_data, selected_user):
    print("This is the selected user:")
    keys = list(users_data.keys())
    print("Favourite genres:")
    for g in users_data[keys[int(selected_user)]][0]:
        print("    "+g)
    print("\nFilms:")
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
        {"role": "user", "content": INTRO_STRING_GENRES + genres + "]." + END_STRING + test_films + "]."}
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
        {"role": "user", "content":SYSTEM_PROMPT + INTRO_STRING_GENRES + genres +"]. " + END_STRING + test_films + "]."}
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
        {"role": "user", "content": INTRO_STRING_FILMS + films + "]." + END_STRING + test_films + "]."}    
        ]]
    return dialogs

def make_dialog_two_two(user, test_user):
    selected_films = [film for film, rate in user[1].items() if rate in {"4.0","5.0"}]
    random.shuffle(selected_films)
    films = "; ".join(selected_films)
    test_films_list = [film for film, rate in user[1].items() if rate in {"1.0", "2.0", "3.0","4.0" ,"5.0"}]
    random.shuffle(test_films_list)
    test_films ="; ".join(test_films_list)
    dialogs: List[Dialog] = [[
        {"role": "user", "content":SYSTEM_PROMPT + INTRO_STRING_FILMS + films + "]." + END_STRING + test_films + "]." }    ]]
    return dialogs
        

if __name__ == "__main__":
    fire.Fire(main)
