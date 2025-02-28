import json
import re
import os

def transform_data(input_data):
    """
    Extracts ID, file name, rock entities, and mineral entities from the input data.
    """
    ID = input_data["ID"]
    file = input_data["file"].split('/')[-1]

    # Extract rock and mineral entities from the 'answer' field
    answer = input_data["answer"]
    #answer=answer.replace('\n','').replace('\r','')
    roc_match = re.search(r'岩石实体：([^；]*)', answer)
    min_match = re.search(r'矿物实体：([^。]*)', answer)

    ROC = extract_entities(roc_match)
    MIN = extract_entities(min_match)

    return {
        "ID": ID,
        "file": file,
        "ROC": ROC,
        "MIN": MIN
    }

def extract_entities(match):
    """
      Extracts a list of entities from the match result.
    """
    if match:
        entities_str = match.group(1).split('\n')[0]
        return [] if entities_str == '无' else re.split(r'[、，]', entities_str)
    return []

def read_and_transform_data(input_file):
    """
     Reads the input file and transforms the data.
    """
    transformed_data = []
    with open(input_file, 'r', encoding='utf-8') as infile:
        for line in infile:
            try:
                data = json.loads(line)
                transformed_data.append(transform_data(data))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line: {line}\n{e}")
    return transformed_data

def save_transformed_data(transformed_data, output_file):
    """
     Saves the transformed data to an output file.
    """
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for dict_item in transformed_data:
            outfile.write(json.dumps(dict_item, ensure_ascii=False) + "\n")

def main():
    # Input and output file paths
    input_json = "../../../recog_result/claude-3-5-sonnet-20240620_baseline.json"
    out_json_dir = "../"
    out_json_file = os.path.join(out_json_dir, "entities.json")

    # Create output directory if it does not exist
    os.makedirs(out_json_dir, exist_ok=True)

    # Read and transform data
    transformed_data = read_and_transform_data(input_json)

    # Save the transformed data to the output file
    save_transformed_data(transformed_data, out_json_file)

    print("Transformation complete!")

if __name__ == "__main__":
    main()