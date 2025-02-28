import json
import os


def load_json_lines(file_path):
    """
    Read a JSON file line by line and return a list of parsed data.

    """
    data = []
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            try:
                data.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON on line: {line}\n{e}")
    return data


def match_annotations_with_predictions(annotations, predictions):
    """
     Match data from annotations and predictions, and return a list of matched results.
    """
    prediction_dict = {item['file']: item for item in predictions}
    matched_data = []

    for annotation in annotations:
        file_name = annotation['file']
        if file_name in prediction_dict:
            matched_prediction = prediction_dict[file_name]
            matched_data.append({
                'annotation': annotation,
                'prediction': matched_prediction
            })

    return matched_data


def save_json(data, file_path):
    """
     Save the data to the specified JSON file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as output_file:
        json.dump(data, output_file, ensure_ascii=False, indent=4)


def main():
    # Read the annotation.json file
    annotations = load_json_lines('../../../../data/test_anno.json')

    # Read the prediction.json file
    prediction_json_dir = ".."
    prediction_json_file = os.path.join(prediction_json_dir, "entities.json")

    predictions = load_json_lines(prediction_json_file)

    # Match data from annotations and predictions
    matched_data = match_annotations_with_predictions(annotations, predictions)

    # Output the matching results
    for match in matched_data:
        print("Annotation:", match['annotation'])
        print("Prediction:", match['prediction'])
        print()

    # Save the matched results to a new JSON file
    out_json_file = os.path.join(prediction_json_dir, "matched_result.json")
    save_json(matched_data, out_json_file)

    print("Matching complete!")


if __name__ == "__main__":
    main()
