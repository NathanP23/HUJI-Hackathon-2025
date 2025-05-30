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
                result = mml_func(cur_prompts[mml_name])
                answer = result['answer']
                others_strengths = result['strengths']
                others_weaknesses = result['weaknesses']

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

    return jsons

if __name__ == "__main__":
    from server import start_server
    start_server(main)
