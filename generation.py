import os

from vllm import LLM, SamplingParams
from load_data import load_data_RealToxicityPrompts, load_data_stereotype, load_data_ethics, load_data_halu, load_data_fairness, load_data_sycophancy, load_data_privacy, load_data_robust
from prompts import toxicity_single_prompt, stereotype_single_prompt, ethics_single_prompt, halu_single_prompt, fairness_single_prompt, sycophancy_single_prompt, privacy_single_prompt, robust_single_prompt
import json
import jsonlines
import argparse
import re
import math
import random
random.seed(42)

def pipeline(llm, aspect, method, model, turn):

	if aspect == 'toxicity':
		data = load_data_RealToxicityPrompts()
	elif aspect == 'ethics':
		shorts, longs = load_data_ethics()
		data = shorts + longs
	elif aspect == 'stereotype':
		data, target_groups = load_data_stereotype()
	elif aspect == 'hallucination':
		data = load_data_halu()
	elif aspect == 'fairness':
		data = load_data_fairness()
	elif aspect == 'sycophancy':
		data = load_data_sycophancy()
	elif aspect == 'privacy':
		data, gt = load_data_privacy()
	elif aspect == 'robustness':
		data = load_data_robust()

	outs = []
	with jsonlines.open('./output/%s_%s_%s_%s.json'%(model.split("/")[-1], aspect, method, turn), 'w') as f:
		total_num_batches = math.ceil(len(data)/BATCH_SIZE)
		for i in range(total_num_batches):
			batch = data[i*BATCH_SIZE:(i+1)*BATCH_SIZE]
			if aspect == 'toxicity' and method == 'ours' and turn == 'single':
				prompts = [ toxicity_single_prompt.format(prompt=prompt) for prompt in batch ]

			elif aspect == 'ethics' and method == 'ours' and turn == 'single':
				prompts = [ ethics_single_prompt.format(prompt=prompt) for prompt in batch ]

			elif aspect == 'stereotype' and method == 'ours' and turn == 'single':
				prompts = [stereotype_single_prompt.format(prompt=prompt) for prompt in batch]

			elif aspect == 'hallucination' and method == 'ours' and turn == 'single':
				prompts = [ halu_single_prompt.format(knowledge=item["knowledge"], question=item["question"], answer_1=item["right_answer"], answer_2=item["hallucinated_answer"]) for item in batch ]	

			elif aspect == 'fairness' and method == 'ours' and turn == 'single':
				prompts = [fairness_single_prompt.format(description=item['description']) for item in batch]

			elif aspect == 'sycophancy' and method == 'ours' and turn == 'single':
				prompts = [sycophancy_single_prompt.format(description=". ".join(item.split("\n\n")[0].split(". ")[-2:])) for item in batch]

			elif aspect == 'privacy' and method == 'ours' and turn == 'single':
				prompts = [privacy_single_prompt.format(context=item[0].strip(), question_1=item[1], answer_1=item[2], question_2=item[3]) for item in batch]

			elif aspect == 'robustness' and method == 'ours' and turn == 'single':
				prompts = [robust_single_prompt.format(input_1=item['cf_example'], answer_1=item['cf_label'], input_2=item['input']) for item in batch]

			else:
				pass

			print("begin generation")
			outputs = llm.generate(prompts, sampling_params)

			# Print the outputs.
			results = []
			for output in outputs:
				prompt = output.prompt
				generated_text = output.outputs[0].text
				print(f"Prompt: {prompt!r}, Generated text: {generated_text!r}")
				print("===============")
				results.append(generated_text)

			for inp, ou in zip(batch, results):
				f.write({"input": inp, "output": ou})

					
def parse_args():

	parser = argparse.ArgumentParser('LLM Eval')
	parser.add_argument('--method', required=True, type=str)
	parser.add_argument('--model', required=True, default="meta-llama/Llama-2-7b-chat-hf")
	parser.add_argument('--aspect', required=True, type=str, choices=["toxicity", "stereotype", "ethics", "hallucination", "fairness", "sycophancy", "privacy", "robustness"])
	parser.add_argument('--turn', required=True, type=str, choices=["single", "multi"])
	parser.add_argument('--num_gpu', required=True, type=int)
	
	return parser.parse_args()


sampling_params = SamplingParams(temperature=0, top_p=1, max_tokens=128)

BATCH_SIZE = 10

def main():

	args = parse_args()
	method = args.method
	model = args.model
	aspect = args.aspect 
	turn = args.turn

	llm = LLM(model=model, tensor_parallel_size=args.num_gpu)  # modify tensor_parallel_size for more GPUs

	pipeline(llm, aspect, method, model, turn)


main()


