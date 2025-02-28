import json
import re
import os

# Define regular expressions for extracting rock and mineral entities
rock_pattern = re.compile(r'\[([^\[\]]+)\]')
mineral_pattern = re.compile(r'<([^<>]+)>')

def read_json_lines(file_path):
    """
     Read a JSON file line by line and return a list of parsed data.
    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"JSON decoding failed: {e} for line: {line}")
    return data

def process_data(data):
    """
    Process each entry in the data to extract rock and mineral entities.
    """
    processed_data = []
    for item in data:
        answer_text = item['answer']
        file_path = item['file']
        ID = item['ID']

        # Extract rock entities using the defined regex pattern
        rocks = rock_pattern.findall(answer_text)

        # Extract mineral entities using the defined regex pattern
        minerals = mineral_pattern.findall(answer_text)

        # Create a result dictionary with the processed data
        result_item = {
            "ID": ID,
            "file": file_path.split('/')[-1],  # Keep only the filename from the full path
            "ROC": rocks,
            "MIN": minerals
        }

        # Add the processed item to the result list
        processed_data.append(result_item)
    return processed_data

def save_processed_data(processed_data, output_file):
    """
     Save the processed data into a new JSON file.
    """
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as outfile:
        for dict_item in processed_data:
            outfile.write(json.dumps(dict_item, ensure_ascii=False) + "\n")
    print("Conversion complete!")

def main():
    # Input and output file paths
    input_json = "../../../recog_result_swap_labeling_symbols/gpt-4o-mini_geoprompted1.json"
    out_json_dir = "../"
    out_json_file = os.path.join(out_json_dir, "entities.json")
    # Read the input JSON file
    data = read_json_lines(input_json)

    # Process the data to extract entities
    processed_data = process_data(data)

    # Output the processed results (optional)
    for result in processed_data:
        print(result)

    # Save the processed data into the output file
    save_processed_data(processed_data, out_json_file)

if __name__ == "__main__":
    main()
