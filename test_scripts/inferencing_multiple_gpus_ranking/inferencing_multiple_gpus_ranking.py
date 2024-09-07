# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

from typing import List, Optional

import random
import fire
import json
import datetime

import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

INTRO_STRING_GENRES = "These are my favourite genres: ["
INTRO_STRING_MOVIES = "These are my favourite movies: ["
END_STRING = ""
SYSTEM_PROMPT = "[INST] <<SYS>>\n You are a movie ranking system. You will receive a list of movies that you will have to sort based on input genres. You will output the first 10 movies that are the best among those in input based on the given genres. The order of the movies in input is random and does not represent an ordering by preference.\n<</SYS>>\n"

def main(
    ckpt_dir: str = None,
    tokenizer_path: str = None,
    temperature: float = 0.6,
    top_p: float = 0.9,
    max_seq_len: int = 4096,
    max_batch_size: int = 8,
    max_gen_len: Optional[int] = None,
):
    #tokenizer = AutoTokenizer.from_pretrained("meta-llama/Llama-2-7b-chat-hf")
    #model = AutoModelForCausalLM.from_pretrained("meta-llama/Llama-2-7b-chat-hf",torch_dtype=torch.float16).to("cuda")
    #tokenizer.pad_token = tokenizer.eos_token
    with open('dataset/dataset_after_sixth/from_train.json', 'r') as json_file:
        users_data = json.load(json_file)
    with open('dataset/dataset_after_sixth/from_test.json', 'r') as json_file:
        users_data_test = json.load(json_file)
    selected_user, max_users = get_tests(users_data_test)
    keys = list(users_data_test.keys())
    keys = list(users_data_test.keys())
    results = {}
    while selected_user < max_users:
        prompt = make_prompt(users_data_test[keys[int(selected_user)]])
        #Righe per gpu singola
        '''model_inputs = tokenizer(prompt, return_tensors="pt", padding=True).input_ids.to("cuda")
        generated_ids = model.generate(input_ids=model_inputs)[0]'''
        #Inserisco qui righe per multi-gpu, verificare che siano corrette
        inputs = tokenizer(list(prompts_batch), return_tensors="pt", padding=True)
        input_ids_tok = inputs["input_ids"].to("cuda")
        attn_masks = inputs["attention_mask"].to("cuda")
        generated_ids = model.generate(input_ids=input_ids_tok, max_new_tokens= 2048, attention_mask=attn_masks)
        #################################
        out = tokenizer.decode(generated_ids.detach().cpu().numpy()[model_inputs.shape[1]:], skip_special_tokens=True)
        results[keys[int(selected_user)]] = out
        selected_user += 1
    folder_name = "ranking_test"
    file_name = "results.json"
    if not(os.path.exists(os.getcwd()+os.sep+folder_name)):
                    os.mkdir("./ranking_test")
    fpJ = os.path.join(os.getcwd()+os.sep+folder_name,file_name)
    with open(fpJ, "w") as outfile: 
        json.dump(results, outfile)


def make_prompt(user):
    genres_list = user[0]
    random.shuffle(genres_list)
    genres = ", ".join(genres_list)
    genres = INTRO_STRING_GENRES + genres + "] .\n"
    selected_movies = [movie for movie, rate in user[1].items()]
    random.shuffle(selected_movies)
    movies = ", ".join(selected_movies)
    movies =INTRO_STRING_MOVIES + movies + "] . [/INST]"
    prompt = SYSTEM_PROMPT + genres + movies
   
    return prompt
    
def get_tests(users_data):      
    answer = "no"
    selected_user = -1
    while (answer == "no"):
        selected_user = input("There are {} users avaibles, select select the user to start from (0 - {})\n".format(len(users_data), len(users_data)-1))
        if int(selected_user) < 0 or int(selected_user) > len(users_data)-1:
            print("Wrong answer, please try again")
        else:
            print_user(users_data, selected_user)
            answer = input("Do you want to select this user? (yes/no)\n")
            if (answer != "yes" and answer != "no"):
                print("Wrong answer, please try again")
    
    return (int(selected_user), len(users_data))

def print_user(users_data, selected_user):
    print("This is the selected user:")
    keys = list(users_data.keys())
    print("Favourite genres:")
    for g in users_data[keys[int(selected_user)]][0]:
        print("    "+g)
    print("\nMovies:")
    for key, rate in users_data[keys[int(selected_user)]][1].items():
        print(f'    Name: {key}, Rate: {rate}')
    

      

if __name__ == "__main__":
    fire.Fire(main)
