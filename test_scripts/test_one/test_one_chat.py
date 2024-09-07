# Copyright (c) Meta Platforms, Inc. and affiliates.
# This software may be used and distributed according to the terms of the Llama 2 Community License Agreement.

from typing import List, Optional

import fire
import sys
from llama import Llama, Dialog
import os
import torch
# ONLY FOR WINDOWS ==========>
os.environ['PL_TORCH_DISTRIBUTED_BACKEND'] = 'gloo'
os.environ['NCCL_DEBUG'] = 'INFO'
torch.distributed.init_process_group(backend="gloo")
# ONLY FOR WINDOWS ==========>


def main(
    ckpt_dir: str,
    tokenizer_path: str,
    temperature: float = 0.6,
    top_p: float = 0.9,
    max_seq_len: int = 4096,
    max_batch_size: int = 8,
    max_gen_len: Optional[int] = None,
):
    """
    Entry point of the program for generating text using a pretrained model.

    Args:
        ckpt_dir (str): The directory containing checkpoint files for the pretrained model.
        tokenizer_path (str): The path to the tokenizer model used for text encoding/decoding.
        temperature (float, optional): The temperature value for controlling randomness in generation.
            Defaults to 0.6.
        top_p (float, optional): The top-p sampling parameter for controlling diversity in generation.
            Defaults to 0.9.
        max_seq_len (int, optional): The maximum sequence length for input prompts. Defaults to 512.
        max_batch_size (int, optional): The maximum batch size for generating sequences. Defaults to 8.
        max_gen_len (int, optional): The maximum length of generated sequences. If None, it will be
            set to the model's max sequence length. Defaults to None.
    """
    history = []
    generator = Llama.build(
        ckpt_dir=ckpt_dir,
        tokenizer_path=tokenizer_path,
        max_seq_len=max_seq_len,
        max_batch_size=max_batch_size,
    )

    value = "4"
    while(value != "1" and value != "3"):
        value = input("Do you want to chat?(y=1/n=3)\n")
        if (value != "1" and value != "3"):
            print("Wrong answer, please try again")

    while (value == "1" or value == "2"):
        if int(value) == 2:
            history.clear()
        if history == []:
            more_info = input(
                "Write special commands such as:\n *Ways that the AI should use to reply\n *Personal preferences if You are gonna ask something that should use your preferences\n *Press Enter if none\n")
        question = input("Write the question\n")
        if more_info == "":
            if history != []:
                if int(value) == 1:
                    history[-1].append({"role": "user", "content": question})
                else:
                    history.append([{"role": "user", "content": question}])
                dialogs: List[Dialog] = history
            else:
                history.append([{"role": "user", "content": question}])
                dialogs: List[Dialog] = history
        else:
            if history != []:
                if int(value) == 1:
                    history[-1].append({"role": "user", "content": question})
                else:
                    history.append([{"role": "system", "content": more_info}])
                    history[-1].append({"role": "user", "content": question})
                dialogs: List[Dialog] = history
            else:
                history.append([{"role": "system", "content": more_info}])
                history[-1].append({"role": "user", "content": question})
                dialogs: List[Dialog] = history
        results = generator.chat_completion(
            dialogs,  # type: ignore
            max_gen_len=max_gen_len,
            temperature=temperature,
            top_p=top_p,
        )
        for dialog, result in zip(dialogs, results):
            for msg in dialog:
                print(f"{msg['role'].capitalize()}: {msg['content']}\n")
            print(
                f"> {result['generation']['role'].capitalize()}: {result['generation']['content']}"
            )
            history[-1].append(
                {"role": result['generation']['role'], "content": result['generation']['content']})
            print("\n==================================\n")
        more_info == ""
        value = input(
            "Select your choise:\n1)Do you want to continue this discussion?\n2)Do you want to start a new conversation?\n3)Exit\n")


if __name__ == "__main__":
    fire.Fire(main)
