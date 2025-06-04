import re
from typing import Tuple, Dict
from LLMs.claude import ask_claude
from LLMs.gemini import ask_gemini
from LLMs.gpt import ask_gpt
from LLMs.helper import *

class MML:
    def __init__(self, name: str):
        self.name = name

MML_LIST = {
    "gpt": ask_gpt,
    "claude": ask_claude,
    "gemini": ask_gemini
    }

def create_final_decision_prompt(json_list):
    """
    Creates a comprehensive prompt for making a final decision based on 
    multiple analyzed answers with their strengths and weaknesses.
    
    Args:
        json_list: List of dictionaries, each containing:
            - "weakness": list of weaknesses of the answer
            - "strength": list of strengths of the answer  
            - "old answer": the original answer being analyzed
            - "original_question": the original question
    
    Returns:
        str: A formatted prompt for final decision making
    """
    
    if not json_list:
        return "No answers provided for analysis."
    
    # Get the original question (should be the same for all entries)
    original_question = json_list[0].get("original_question", "Unknown question")
    
    prompt = f"""Based on the analysis of multiple answers to the following question, please provide a final, comprehensive response:

ORIGINAL QUESTION: {original_question}

ANALYSIS OF CANDIDATE ANSWERS:
"""
    
    for i, answer_data in enumerate(json_list, 1):
        old_answer = answer_data.get("old answer", "No answer provided")
        strengths = answer_data.get("strength", [])
        weaknesses = answer_data.get("weakness", [])
        
        prompt += f"""
--- ANSWER {i} ---
CONTENT: {old_answer}

STRENGTHS:"""
        
        if strengths:
            for strength in strengths:
                prompt += f"\n• {strength}"
        else:
            prompt += "\n• No strengths identified"
            
        prompt += f"\n\nWEAKNESSES:"
        
        if weaknesses:
            for weakness in weaknesses:
                prompt += f"\n• {weakness}"
        else:
            prompt += "\n• No weaknesses identified"
        
        prompt += "\n"
    
    prompt += """
TASK: 
Please synthesize the best elements from all analyzed answers while addressing their identified weaknesses. Create a final response that:

1. Incorporates the strongest points from each answer
2. Addresses or mitigates the identified weaknesses
3. Provides a comprehensive and well-rounded response to the original question
4. Maintains accuracy and clarity throughout

Your final answer should represent the best possible response by learning from both the strengths and limitations of the candidate answers."""
    
    return prompt
        

async def main(user_question):
    from Prompt_Engineer.prompt_engineer import OptimizeRawPrompt
    # user_question = input("Enter your prompt: ")


    # prompt -> optimized prompt
    first_prompt = OptimizeRawPrompt(user_question)
    dept = 1#int(input("Enter your dept of rethinking: "))
    cur_prompts = {mml: first_prompt for mml in MML_LIST.keys()}
    jsons = []
    improvement = False
    while dept >= 0:
        names = []
        answers = {}
        weaknesses = {mml : [] for mml in MML_LIST.keys()}
        strengths = {mml : [] for mml in MML_LIST.keys()}

        for mml_name, mml_func in MML_LIST.items():
            # optimized prompt -> answer, weakness, strength
            if not improvement:
                # to string
                answer = mml_func(cur_prompts[mml_name], format_response=improvement)
            else:
                # to dict
                # answer, weakness, strength = mml_func(cur_prompts[mml_name])
                try:
                    result = mml_func(cur_prompts[mml_name])
                    answer = result['answer']
                    others_strengths = result['strengths']
                    others_weaknesses = result['weaknesses']
                except Exception as e:
                    print(f"Error in {mml_name}: {e}")
                    answer = "Error generating response"
                    others_strengths = {}
                    others_weaknesses = {}
                
                for key, val in others_weaknesses.items():
                    weaknesses[key].append(val)

                for key, val in others_strengths.items():
                    strengths[key].append(val)

            names.append(mml_name)
            answers[mml_name] = answer

        names_to_answers = {}
        for name in names:
            names_to_answers[name] = {name : {}}
            for name2, answer in zip(names, answers.values()):
                if name2 != name:
                    names_to_answers[name][name2] = answer

        jsons = [{"weakness" : weaknesses[name],
                  "strength" : strengths[name],
                  "names to answers" : names_to_answers[name],
                  "name" : name,
                  "old answer" : answers[name],
                  "original_question" : first_prompt} for name, answer in zip(names, answers)]
        
        print("JSONs:")
        from server import send_data_to_all
        for json in jsons:
            print("Sending JSON to all clients:", json)
            await send_data_to_all(json)
            print(json)

        for mml, json in zip(MML_LIST, jsons):
            # JSON: answer, weakness, strength -> prompt to improve next iteration with new answer
            cur_prompts[mml] = generate_improvement_prompt(json)
        improvement = True
        dept -= 1

    final_prompt = create_final_decision_prompt(jsons)
    final_answer = ask_gpt(final_prompt, format_response=False)
    final_json = {"name" : "gpt", "old answer" : final_answer}
    await send_data_to_all(final_json)

if __name__ == "__main__":
    from server import start_server
    start_server(main)
