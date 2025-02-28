import json
from difflib import SequenceMatcher

def calculate_similarity(a, b):
    """
    Calculate the similarity between two strings.
    """
    return SequenceMatcher(None, a, b).ratio()

def process_matching(annotation, prediction, key):
    """
    Process the matching logic, returning results that include exact matches, partial matches, misses, and predictions that are not in the ground truth.
    """
    result_dict = {
        "full_matched": [],
        "matched": [],
        "miss": [],
        "not_in_ground_truth": []
    }

    anno_list = annotation[key]
    pred_list = prediction[key]

    for anno_item in anno_list:
        found_full_match = False
        found_partial_match = False

        # Check for full match
        if anno_item in pred_list:
            result_dict["full_matched"].append(anno_item)
            pred_list.remove(anno_item)
            found_full_match = True

        # Check for partial match if no full match found
        if not found_full_match:
            for pred_item in pred_list:
                if calculate_similarity(anno_item, pred_item) >= 0.75:
                    result_dict["matched"].append(anno_item)
                    pred_list.remove(pred_item)
                    found_partial_match = True
                    break

        # If no match found, add to miss
        if not found_full_match and not found_partial_match:
            result_dict["miss"].append(anno_item)

    # Any remaining in pred_list are not in ground truth
    result_dict["not_in_ground_truth"].extend(pred_list)

    return result_dict

def load_json(file_path):
    """
     Read a JSON file and return the data.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(data, file_path):
    """
     Save the data to the specified JSON file.
    """
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def main():
    # Set file paths
    matched_json_dir = "../"  #"inter_3.5_results/" "inter_4o_results/" "category_pre_directly_inter_4o_results/"
    matched_json_file = f"{matched_json_dir}/matched_result.json"
    out_json_file = f"{matched_json_dir}/final_matched_result.json"

    # Read matched_results.json file
    matched_results = load_json(matched_json_file)

    # Store the final results
    final_results = []

    for match in matched_results:
        annotation = match["annotation"]
        prediction = match["prediction"]

        roc_result_dict = process_matching(annotation, prediction, "ROC")
        min_result_dict = process_matching(annotation, prediction, "MIN")

        final_results.append({
            "ID": annotation["ID"],
            "file": annotation["file"],
            "ROC_result": roc_result_dict,
            "MIN_result": min_result_dict
        })

    # Output matching results
    for result in final_results:
        print(json.dumps(result, ensure_ascii=False, indent=4))

    # Save the final results to a new JSON file
    save_json(final_results, out_json_file)
    print("Processing complete!")

if __name__ == "__main__":
    main()
