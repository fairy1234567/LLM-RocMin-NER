# -*- coding: utf-8 -*-
import os
import json
import time
from tqdm import tqdm
import openai
from tenacity import retry, stop_after_attempt, wait_random_exponential

# Set up the basic information for OpenAI API
openai.api_key = ""  # Replace with your OpenAI API key

# Entity labeling prompt
entity_label_prompt = [{'role': 'system',
                       'content': """
你将会标注文本中的岩石和矿物实体。标注规则如下：
1. 用尖括号'<'和'>'标记岩石实体。
2. 用中括号'['和']'标记矿物实体。
3. 如果未识别出岩石以及矿物实体，则直接输出原句。

典型易错误识别为岩石的实体如下：岩体、岩脉、岩群、岩带、岩石、安山质、地层(XXX组、XXX群、XXX系)、亚带、垂体
典型易错误识别为矿物的实体如下：矿物、Fe、FeO
下面的修饰不作为岩石实体的一部分：位置（”纳巴乃嘎闪长岩“中的岩石实体应为”闪长岩“）、地层（”申拉组火山岩“中的岩石实体应为”火山岩“）、沉积相（”泻湖相砂页岩“中的岩石实体应为”砂页岩“）
下面的修饰应该作为岩石实体的一部分：颜色（”深灰色”作为深灰色钙质页岩“的一部分）、次要矿物（“英安质”作为“英安质晶屑熔结凝灰岩”的一部分）、结构（“细晶”作为“中薄层细晶白云岩”的一部分）、构造（“中薄层状”作为“褐色中薄层状粉砂质板岩”的一部分）

以下是一些示例：
示例1：
输入：该地区主要岩石类型为石英二长岩和花岗岩，常见矿物包括石英和长石。
输出：该地区主要岩石类型为<石英二长岩>和<花岗岩>，常见矿物包括[石英]和[长石]。

示例2：
输入：玄武岩是一种常见的火成岩，含有橄榄石、辉石等矿物。
输出：<玄武岩>是一种常见的火成岩，含有[橄榄石]、[辉石]等矿物。
"""
}]

# Load data from a JSON file
def load_list_json(file_path):
    with open(file_path, 'r', errors='ignore', encoding="utf-8") as f:
        return json.load(f)

# Load data from a TXT file
def load_txt_data(file_path, sep=":"):
    with open(file_path, 'r', errors='ignore', encoding="utf-8") as f:
        data_list = []
        item = {}
        id=1
        for i, line in enumerate(f, 1):
            line = line.strip()
            if i % 2 == 1:
                item["ID"]=id
                item["file"] = line.split(sep)[1].strip()
            else:
                item["text"] = line.split("文本内容：")[1].strip()
                data_list.append(item)
                item = {}
                id+=1
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
                        print(f"JSON decoding failed: {e} for line: {line}")
    return res_dict_list


# Call OpenAI API to get annotation results
@retry(wait=wait_random_exponential(min=1, max=60), stop=stop_after_attempt(5))
def get_roc_min_anno(row, conv_recog_prompt, text_key="text", model="gpt-3.5-turbo", num_attempts=3):
    text = row[text_key]
    this_conv_prompt = conv_recog_prompt.copy()
    this_conv_prompt.append({'role': 'user', 'content': '句子: ' + text})
    print(this_conv_prompt)
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
    res_dict = {'answer': answer,"prompt":this_conv_prompt}
    res_dict.update(row)
    return res_dict

# Main function
def main():
    data_file = "../data/test.txt"
    res_dir = "../recog_result"
    model = "gpt-4o-2024-08-06"  # "gpt-4o" "gpt-3.5-turbo" "claude-3-5-sonnet-20240620" "gpt-4o-2024-08-06"
    res_file = f"{res_dir}/{model}_geoprompted2.json"

    data_list = load_txt_data(data_file)

    os.makedirs(res_dir, exist_ok=True)
    res_dict_list = read_res_file(res_file)
    process_ids = [res_dict['ID'] for res_dict in res_dict_list]
    cur_data_list = [item for item in data_list if item["ID"] not in process_ids]
    print("Number of sentences to be recognized by the model:", len(cur_data_list))

    count = 0
    for i, item in tqdm(enumerate(cur_data_list), total=len(cur_data_list)):
        res_dict = get_roc_min_anno(item, entity_label_prompt, model=model, text_key="text")
        with open(res_file, 'a', encoding="utf-8") as f:
            f.write(json.dumps(res_dict, ensure_ascii=False) + "\n")
        count += 1
        if count == 199:
            break

if __name__ == "__main__":
    main()