# -*- coding: utf-8 -*-
import os
import json
import time
from tqdm import tqdm
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

# 设置OpenAI API的基本信息
openai.api_key = ""  # 需要替换为你的OpenAI API密钥

# 定义实体识别和标注的提示内容
entity_extraction_prompt = [{'role': 'system',
                             'content': "需要你识别出所给句中所有的岩石实体和矿物实体。回答格式为：岩石实体：实体1，实体2；矿物实体：实体1，实体2。如果没有则回答：岩石实体：无；矿物实体：无。"}]


# 加载JSON文件数据
def load_list_json(file_path):
    with open(file_path, 'r', errors='ignore', encoding="utf-8") as f:
        return json.load(f)

# 加载TXT文件数据
def load_txt_data(file_path, sep=":"):
    with open(file_path, 'r', errors='ignore', encoding="utf-8") as f:
        data_list = []
        item = {}
        id = 1
        for i, line in enumerate(f, 1):
            line = line.strip()
            if i % 2 == 1:
                item["ID"] = id
                item["file"] = line.split(sep)[1].strip()
            else:
                item["text"] = line.split("文本内容：")[1].strip()
                data_list.append(item)
                item = {}
                id += 1
    return data_list

# 读取结果文件
def read_res_file(res_file):
    res_dict_list = []
    if os.path.exists(res_file):
        with open(res_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        res_dict_list.append(json.loads(line))
                    except json.JSONDecodeError as e:
                        print(f"JSON decoding failed: {e} for line: {line}")
    return res_dict_list

# 调用OpenAI API获取标注结果
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def get_roc_min(row, conv_recog_prompt, text_key="text", model="gpt-3.5-turbo", num_attempts=3):
    text = row[text_key]
    this_conv_prompt = conv_recog_prompt.copy()
    this_conv_prompt.append({'role': 'user',
                             'content': '句子: '+text})
    completion = openai.ChatCompletion.create(
        model=model,
        messages=this_conv_prompt,
        max_tokens=1000,
        temperature=0.2,
        top_p=1,
        n=1,
        presence_penalty=0,
        frequency_penalty=0
    )
    answer = completion.choices[0].message["content"]
    res_dict = {'answer': answer,'prompt':this_conv_prompt}
    res_dict.update(row)
    return res_dict


# 主函数
def main():
    data_file = "../data/test.txt"
    res_dir = "../recog_result"
    model = "gpt-4o-2024-08-06" #"gpt-4o" "gpt-3.5-turbo" "claude-3-5-sonnet-20240620" "gpt-4o-2024-08-06"
    res_file = f"{res_dir}/{model}_baseline.json"

    data_list = load_txt_data(data_file)

    os.makedirs(res_dir, exist_ok=True)
    res_dict_list = read_res_file(res_file)
    process_ids = [res_dict['ID'] for res_dict in res_dict_list]
    cur_data_list = [item for item in data_list if item["ID"] not in process_ids]
    print("需要模型识别的句子个数为：", len(cur_data_list))

    count = 0
    for i, item in tqdm(enumerate(cur_data_list), total=len(cur_data_list)):
        res_dict = get_roc_min(item,entity_extraction_prompt, model=model, text_key="text")
        with open(res_file, 'a', encoding="utf-8") as f:
            f.write(json.dumps(res_dict, ensure_ascii=False) + "\n")
        count += 1
        if count == 199:
            break

if __name__ == "__main__":
    main()