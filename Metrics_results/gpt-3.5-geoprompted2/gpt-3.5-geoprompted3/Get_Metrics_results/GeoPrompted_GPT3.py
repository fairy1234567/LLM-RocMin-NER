# -*- coding: utf-8 -*-
import os
import json
import time
from tqdm import tqdm
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Set up the basic information for OpenAI API
openai.api_key = ""  # Replace with your OpenAI API key


entity_extraction_prompt = [{'role': 'system',
                             'content': "需要你识别出每个实体的类别，类别必须为“岩石”，“矿物”，“其它”三个中的任意一个。回答必须为每个实体的类别，用逗号连接。"}]

# Load data from a JSON file
def load_list_json(file_path):
    with open(file_path, 'r', errors='ignore', encoding="utf-8") as f:
        return json.load(f)

# Load data from a TXT file
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

# Read result file
def read_res_file(res_file):
    res_dict_list = []
    if os.path.exists(res_file):
        with open(res_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        res_dict_list.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        pass
    return res_dict_list

# Call OpenAI API to get annotation results
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def get_category_together(row, conv_recog_prompt,model="gpt-4o"):
    roc_list = row["ROC"]
    min_list=row["MIN"]
    entities_list=roc_list+min_list
    entities="，".join(entities_list)
    this_conv_prompt = conv_recog_prompt.copy()
    answer_list=[]
    this_conv_prompt.append({'role':'user',
                             'content':entities})
    print("prompt:", this_conv_prompt)
    completion = openai.ChatCompletion.create(
        model=model,
        messages=this_conv_prompt,
        max_tokens=1000,
        temperature=0.0,
        top_p=1,
        n=1,
        presence_penalty=0,
        frequency_penalty=0
    )

    answer = completion.choices[0].message["content"]
    print("answer:",answer)

    answer_list.append(answer)
    res_dict = {'answer': answer_list,'entities':entities,"prompt":this_conv_prompt}
    res_dict.update(row)
    return res_dict


# Main function
def main():
    data_dir= ".."
    data_filename = "entities" #"extities_extracted_from_answer"
    data_file=f"{data_dir}/{data_filename}.json"
    data_list = load_data(data_file)

    res_dir = "../cate_confirm_result"
    res_file = f"{res_dir}/cate_confirm_gpt-3.5-turbo.json"
    model="gpt-3.5-turbo" #gpt-3.5-turbo

    os.makedirs(res_dir, exist_ok=True)
    res_dict_list = read_res_file(res_file)
    process_ids = [res_dict['ID'] for res_dict in res_dict_list]
    cur_data_list = [item for item in data_list if item["ID"] not in process_ids]
    print("Number of sentences to be recognized by the model:", len(cur_data_list))

    count = 0
    for i, item in tqdm(enumerate(cur_data_list), total=len(cur_data_list)):
        res_dict = get_category_together(item,entity_extraction_prompt, model=model)
        with open(res_file, 'a', encoding="utf-8") as f:
            f.write(json.dumps(res_dict, ensure_ascii=False) + "\n")
        count += 1
        if count == 198:
            break

if __name__ == "__main__":
    main()