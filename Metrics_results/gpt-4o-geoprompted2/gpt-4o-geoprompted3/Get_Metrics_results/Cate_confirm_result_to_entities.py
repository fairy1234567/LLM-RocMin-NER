# -*- coding: utf-8 -*-
import os
import json
import time
from tqdm import tqdm
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential


def load_list_json(file_path):
    with open(file_path, 'r', errors='ignore', encoding="utf-8") as f:
        return json.load(f)


def load_data(file_path, sep=":"):
    with open(file_path, 'r', errors='ignore', encoding="utf-8") as f:
        data_list = []
        for line in f:
            if line.strip():
                try:
                    data_list.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"JSON decoding failed: {e} for line:{line}")
    return data_list



def get_roc_min(row):
    roc_list = row["ROC"]
    min_list=row["MIN"]
    final_roc_list=[]
    final_min_list=[]
    entities_list=roc_list+min_list
    prediction_list=row["answer"][0].split("，")
    if len(prediction_list)==len(entities_list):
        for i,item in enumerate(prediction_list):
            print(i)
            if item=="岩石":
                final_roc_list.append(entities_list[i])
            elif item=="矿物":
                final_min_list.append(entities_list[i])

    res_dict = {'ID':row["ID"],'file':row["file"],'ROC': final_roc_list,'MIN':final_min_list}

    return res_dict



def main():
    data_dir= "../cate_confirm_result"
    data_filename ="cate_confirm_gpt-4o.json"  #"label_directly_together.json"  "label_with_knowledge_together.json"
    data_file=f"{data_dir}/{data_filename}"
    data_list = load_data(data_file)

    res_dir= ".."
    res_filename="entities.json"
    res_file=f"{res_dir}/{res_filename}"

    for i, item in tqdm(enumerate(data_list), total=len(data_list)):
        res_dict = get_roc_min(item)
        with open(res_file, 'a', encoding="utf-8") as f:
            f.write(json.dumps(res_dict, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()