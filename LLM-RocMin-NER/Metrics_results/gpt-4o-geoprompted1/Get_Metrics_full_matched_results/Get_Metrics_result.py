import json
import os

def calculate_metrics(result_list, key):
    """
        Calculate TP (True Positives), FN (False Negatives), and FP (False Positives) for prediction results.
       """
    TP = len(result_list[key]["full_matched"]) + len(result_list[key]["matched"])
    FN = len(result_list[key]["miss"])
    FP = len(result_list[key]["not_in_ground_truth"])

    return TP, FN, FP

def calculate_precision_recall_f1(TP, FN, FP):
    """
    Calculate precision, recall, and F1 score based on TP, FN, and FP.
    """
    precision = TP / (TP + FP) if TP + FP > 0 else 0
    recall = TP / (TP + FN) if TP + FN > 0 else 0
    f1_score = 2 * (precision * recall) / (precision + recall) if precision + recall > 0 else 0

    return precision, recall, f1_score

def load_json(file_path):
    """
    Read a JSON file and return its data.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_json(data, file_path):
    """
    Save data to the specified JSON file.
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def main():
    # Set file paths
    final_matched_json_dir ="../"
    final_matched_json_file = os.path.join(final_matched_json_dir, "final_full_matched_result.json")
    out_json_dir= "../"
    out_json_filename = "metrics_full_matched_result_calude-3.5-sonnet.json"

    out_json_file = os.path.join(out_json_dir, out_json_filename)
    # Read the final_matched_results.json file
    final_results = load_json(final_matched_json_file)

    # Initialize total counts
    TP_ROC, FN_ROC, FP_ROC = 0, 0, 0
    TP_MIN, FN_MIN, FP_MIN = 0, 0, 0

    # Calculate and accumulate metrics for each result
    for result in final_results:
        tp_roc, fn_roc, fp_roc = calculate_metrics(result, "ROC_result")
        tp_min, fn_min, fp_min = calculate_metrics(result, "MIN_result")

        TP_ROC += tp_roc
        FN_ROC += fn_roc
        FP_ROC += fp_roc

        TP_MIN += tp_min
        FN_MIN += fn_min
        FP_MIN += fp_min
    print(TP_ROC, FN_ROC, FP_ROC)
    print(TP_MIN, FN_MIN, FP_MIN)
    # Calculate precision, recall, and F1 score for ROC and MIN
    precision_roc, recall_roc, f1_roc = calculate_precision_recall_f1(TP_ROC, FN_ROC, FP_ROC)
    precision_min, recall_min, f1_min = calculate_precision_recall_f1(TP_MIN, FN_MIN, FP_MIN)

    # Output the results
    print(f"{final_matched_json_file}:")
    print("ROC - Precision:", precision_roc)
    print("ROC - Recall:", recall_roc)
    print("ROC - F1 Score:", f1_roc)
    print("MIN - Precision:", precision_min)
    print("MIN - Recall:", recall_min)
    print("MIN - F1 Score:", f1_min)

    # Save the results to a new JSON file
    metrics = {
        "ROC": {
            "Precision": precision_roc,
            "Recall": recall_roc,
            "F1 Score": f1_roc
        },
        "MIN": {
            "Precision": precision_min,
            "Recall": recall_min,
            "F1 Score": f1_min
        }
    }

    save_json(metrics, out_json_file)
    print("Save the results to a new JSON file")


if __name__ == "__main__":
    main()