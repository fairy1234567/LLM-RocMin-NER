The repository provides the code and data supporting the paper.

# Data

The "data" folder contains experimental data files. The "test.txt" file includes the file paths and text content for 200 experimental samples. The "test_anno.json" file contains the annotated rock and mineral entities corresponding to these 200 samples.
# Demo

The "Demo" folder includes a simple test file. By adding your own OpenAI API key in the "GeoPrompted_demo.py" file, you can run it directly. The results will be saved in the "recog_result" directory.

# GetResult

The "GetResult" folder contains the code files for calling the large language model (LLM) API and saving the output results. The "GPT_Baseline.py" file is used for direct entity extraction without prompt guidance. The "GeoPrompted_GPT1.py" file is for the initial entity recognition step, while "GeoPrompted_GPT2.py" is used for entity recognition that integrates geological knowledge.

# recog_result

The "recog_result" folder contains the output result files corresponding to the three code files in the "GetResult" folder for different large language models.

# Metrics_results

The "Metrics_results" folder contains the code and result files for obtaining metrics from each JSON file in the "recog_result" folder. For example, in the "claude-3.5-sonnet-geoprompted2" folder, inside the "Get_Metrics_results" subfolder, you should first run the "Get_anno_entities.py" file to extract the rock and mineral entities from the output. Then, run "Get_matched_result.py" to get the initial matching result with the annotations. After that, run "Get_final_matched_result.py" to obtain the final matched result, and finally, run "Get_metrics_result.py" to obtain the metrics. Note: Before running each script, make sure to check the input and output file paths.

## claude-3.5-sonnet-geoprompted2

The "claude-3.5-sonnet-geoprompted2" folder contains another subfolder, "claude-3.5-sonnet-geoprompted3," which stores the code and results for secondary category validation and the metrics code files. Inside the "Get_Metrics_results" subfolder, first run "GeoPrompted_GPT3.py" to get the type validation results for each entity. Then, run "Cate_confirm_result_to_entities.py" to extract the entities that are still classified as rocks or minerals, and generate the "entities.json" file. Next, run "Get_matched_result.py" to obtain the initial matching result, "matched_result.json." After that, run "Get_final_matched_result.py" to get the final matched result, "final_matched_result.json." Finally, run the "Get_Metrics_result.py" file to generate the metrics result, "metrics_result_claude-3.5-sonnet.json." As always, ensure that the input and output file paths are correct before running each script.
