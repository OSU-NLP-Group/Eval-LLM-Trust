import json
import jsonlines
import pandas as pd
import pickle
import os
import random
random.seed(42)

def load_data_robust():
	# SNLI-CAD, counterfacutal example by revising hyphthesis (SNLI-RH)
	path_1 = "./datasets/adv_demonstration/counterfactual/snli_hypothesis_cf/42.jsonl"
	data_1 = []
	with jsonlines.open(path_1, 'r') as reader:
		for obj in reader:
			tmp = {"input": obj['input'].replace("\n", " "), "label": obj['label'], "cf_example": obj['examples'][-1][0].replace("\n", " "), "cf_label": obj['examples'][-1][1]}
			data_1.append(tmp)

	# SNLI-CAD, counterfacutal example by revising premise (SNLI-RP)
	path_2 = "./datasets/adv_demonstration/counterfactual/snli_premise_cf/42.jsonl"
	data_2 = []
	with jsonlines.open(path_2, 'r') as reader:
		for obj in reader:
			tmp = {"input": obj['input'].replace("\n", " "), "label": obj['label'], "cf_example": obj['examples'][-1][0].replace("\n", " "), "cf_label": obj['examples'][-1][1]}
			data_2.append(tmp)

	data = data_1 + data_2

	return data


def load_data_privacy():
	path = "./datasets/privacy/pii/"
	all_files = os.listdir(path)

	filtered_files = [f for f in all_files if "1shotattack_s100_gpt-4" in f]
	print(filtered_files, len(filtered_files))
	data = []
	gt = []
	for file in filtered_files:
		with jsonlines.open(path+file, 'r') as reader:
			for obj in reader:
				tmp = [ele['content'] for ele in obj['prompt']]
				data.append(tmp)
				gt.append(obj['gt'])
	
	return data, gt

def load_data_sycophancy():
	# sycophancy (simple addition statements)
	path = "./datasets/sycophancy-intervention/synthetic_eval_opinionTrue_2500.tsv"
	data = [item for item in pickle.load(open(path, "rb"))]

	return data



def load_data_fairness():
	# adult dataset
	path = "./datasets/fairness/adult_0_200_test_base_rate_0.0.jsonl"
	data = []
	with jsonlines.open(path, 'r') as reader:
		for obj in reader:
			tmp = {"description": obj['input'].split('\n')[0].replace("description:  ", ""), "label": obj['label']}
			data.append(tmp)
	return data

def load_data_halu():
	# Halu dataset for hallucination
	path = "./datasets/HaluEval/qa_data.json"
	data = []
	with jsonlines.open(path, 'r') as reader:
		for obj in reader:
			data.append(obj)

	return data[0:1000] # each element is {"knowledge": "", "question": "", "right_answer": "", "hallucinated_answer": ""}


def load_data_stereotype():

	path = "./datasets/stereotype/stereotype.json"
	opinions = []
	target_groups = []
	with jsonlines.open(path, 'r') as reader:
		for obj in reader:
			opinion = obj['prompt']['text'].split("Here is my statement: ")[1]
			target_group = obj['prompt']['demographic_group_tag']
			if opinion not in opinions:
				opinions.append(opinion)
				target_groups.append(target_group)
	
	return opinions, target_groups


def load_data_RealToxicityPrompts():

	path = "./datasets/toxicity/user_prompts/toxic.jsonl"

	prompts = []
	with jsonlines.open(path) as reader:
		for obj in reader:
			prompt = obj["prompt"]["text"]
			prompts.append(prompt)

	return prompts

def load_data_ethics():

	filename = "./datasets/ethics/commonsense/cm_test.csv"
	data = pd.read_csv(filename)

	labels = data['label'].tolist()
	inputs = data['input'].tolist()
	is_shorts = data['is_short'].tolist()

	shorts = []
	longs = []
	for label, inp, is_short in zip(labels, inputs, is_shorts):
		if is_short:
			if label == 1:
				shorts.append(inp)
		if not is_short:
			if label == 1:
				longs.append(inp)

	return shorts, longs

