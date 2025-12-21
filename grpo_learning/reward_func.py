import re
# def extract_answer(text):
#     answer = text.split("<answer>")[-1]
#     answer = answer.split("</answer>")[0]
#     return answer.strip()
import re


def extract_answer(text):
    # 尝试匹配 <answer> ... </answer>，支持跨行、空白等
    match = re.search(r"<answer>\s*(.*?)\s*</answer>", text, re.DOTALL)
    if match:
        return match.group(1).strip()

    # fallback: 找最后一行纯数字
    lines = text.strip().split('\n')
    for line in reversed(lines):
        line = line.strip()
        if line.isdigit() or (line.startswith('-') and line[1:].isdigit()):
            return line

    # 再 fallback: 提取所有数字，返回最后一个
    numbers = re.findall(r'-?\d+', text)
    if numbers:
        return numbers[-1]

    return ""  # 无法提取
# def mark_num(text):
#     reward = 0
#     if text.count("<think>\n") == 1:
#         reward += 0.125
#
#     if text.count("</think>\n") == 1:
#         reward += 0.125
#
#     if text.count("<answer>\n") == 1:
#         reward += 0.125
#
#     if text.count("</answer>\n") == 1:
#         reward += 0.125
#     return reward
def mark_num(text):
    reward = 0.0
    if "<think>" in text:
        reward += 0.125
    if "</think>" in text:
        reward += 0.125
    if "<answer>" in text:
        reward += 0.125
    if "</answer>" in text:
        reward += 0.125
    return reward

def get_gsm8k_target(ans_str):
    match = re.search(r'####\s*(\d+)', str(ans_str))
    return match.group(1) if match else re.findall(r'\d+', str(ans_str))[-1]
def correctness_reward(prompts, responses, answers):
    extracted_responses = [extract_answer(r) for r in responses]
    targets = [get_gsm8k_target(a) for a in answers]
    # print(f"Question:\n{prompts[0]}", f"\nAnswer:\n{answers[0]}", f"\nOutput:\n{responses[0]}",
    #       f"\nExtract_answer:\n{extracted_responses[0]}")
    # print(f"Extracted: {extracted_responses[0]}, Target: {targets[0]}")
    return [2.0 if e == t else 0.0 for e, t in zip(extracted_responses, targets)]
# # 生成答案是否正确的奖励
# def correctness_reward(prompts, responses, answers):
#     extracted_responses = [extract_answer(r) for r in responses]
#     # print(f"Question:\n{prompts[0]}", f"\nAnswer:\n{answers[0]}", f"\nOutput:\n{responses[0]}", f"\nExtract_answer:\n{extracted_responses[0]}")
#     return [2.0 if response == str(ans) else 0.0 for response, ans in zip(extracted_responses, answers)]

# 生成答案是否是数字的奖励（单纯依赖结果是否正确进行奖励，条件很苛刻，会导致奖励比较稀疏，模型难以收敛，所以加上答案是否是数字的奖励，虽然答案错误，但是至少生成的是数字（对于数学问题），也要给予适当奖励）
def digit_reward(prompts, responses, answers):
    extracted_responses = [extract_answer(r) for r in responses]
    return [0.5 if response.isdigit() else 0.0 for response in extracted_responses]

# 格式奖励
def hard_format_reward(prompts, responses, answers):
    pattern = r"^<think>\n.*?\n</think>\n<answer>\n.*?\n</answer>\n$"
    matches = [re.match(pattern, response) for response in responses]
    return [0.5 if match else 0.0 for match in matches]

# 标记奖励（改善格式奖励稀疏问题）
def mark_reward(prompts, responses, answers):
    return [mark_num(response) for response in responses]