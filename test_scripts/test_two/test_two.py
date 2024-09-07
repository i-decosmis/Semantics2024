# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

from typing import List, Optional

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

INTRO_STRING_GENRES = "This are my favourite film genres: "
INTRO_STRING_FILMS = "This are my favourite film: "
INPUT_PROMPT = "Suggest me 50 films based on my favourite genres, do not write film trama, just the name"

def main(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0.6,
    top_p: float = 0.9,
    max_seq_len: int = 4096,
    max_batch_size: int = 8,
    max_gen_len: Optional[int] = None,
):
    with open('dataset/dataset_before_sixth/from_test.json', 'r') as json_file:
        users_data = json.load(json_file)
    
    test_type = "4"
    test_properties = "4"
    test_type, test_properties, selected_user = get_tests(test_type, test_properties, users_data)
    if test_type == 3:
        print("Exit...")
    else:
        keys = list(users_data.keys())
        dialogs: List[Dialog] = make_dialog(test_type, test_properties, users_data[keys[int(selected_user)]])
        generator = Llama.build(
            ckpt_dir=ckpt_dir,
            tokenizer_path=tokenizer_path,
            max_seq_len=max_seq_len,
            max_batch_size=max_batch_size,
        )                
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

def make_dialog(test_type, test_properties, user):
    if test_type == 1:
        if test_properties == 1:
            dialogs: List[Dialog] = make_dialog_one_one(user)
            return dialogs
        else:
            dialogs: List[Dialog] = make_dialog_one_two(user)
            return dialogs
    else:
        if test_properties == 1:
            dialogs: List[Dialog] = make_dialog_two_one(user)
            return dialogs
        else:
            dialogs: List[Dialog] = make_dialog_two_two(user)
            return dialogs

        
def make_dialog_one_one(user):
    genres = ", ".join(user[0])
    dialogs: List[Dialog] = [[
        {"role": "system", "content": INTRO_STRING_GENRES + genres},
        {"role": "user", "content": INPUT_PROMPT}
    ]]
    return dialogs

def make_dialog_one_two(user):
    genres = ", ".join(user[0])
    dialogs: List[Dialog] = [[
        {"role": "user", "content": INTRO_STRING_GENRES + genres +". " + INPUT_PROMPT}
    ]]
    return dialogs

def make_dialog_two_one(user):
    selected_films = [film for film, rate in user[1].items() if rate in {"4.0","5.0"}]
    films = ", ".join(selected_films)
    dialogs: List[Dialog] = [[
        {"role": "system", "content": INTRO_STRING_FILMS + films},
        {"role": "user", "content": INPUT_PROMPT}    ]]
    return dialogs

def make_dialog_two_two(user):
    selected_films = [film for film, rate in user[1].items() if rate in {"4.0","5.0"}]
    films = ", ".join(selected_films)
    dialogs: List[Dialog] = [[
        {"role": "user", "content": INTRO_STRING_FILMS + films + ". " + INPUT_PROMPT}    ]]
    return dialogs
        

if __name__ == "__main__":
    fire.Fire(main)
