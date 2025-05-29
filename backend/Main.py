import re
from typing import Tuple, Dict

class MML:
    def __init__(self, name: str):
        self.name = name

    def get_answer(self, question: str) -> str:
        """parts = question.split("|")
        ans = ""
        for part, boundaries in zip(parts, ALL_BOUNDARIES):
            ans += boundaries[0] + part + boundaries[1]

        return self.name + ans"""
        return (
        "{+{This is the answer}+}"
        "[+[(+(claud<-->Could be clearer)+) (+(gemini<-->Too short)+)]+]"
        "<+<(+(claud<-->Well structured)+) (+(gemini<-->Concise)+)>+>"
    )
from LLMs.claude import ask_claude
from LLMs.gemini import ask_gemini
from LLMs.gpt import ask_gpt
MML_LIST = {
    "gpt": ask_gpt,
    "claude": ask_claude,
    "gemini": ask_gemini
    }



# def split_response(text: str) -> Tuple[str, Dict[str, str], Dict[str, str]]:
#     """
#     Parses a structured string of the format:
#     "{+{answer}+}[+[(+(name<-->weakness)+) ...]+]<+<(+(name<-->strength)+) ...>+>"

#     Returns:
#         - answer (str)
#         - weaknesses (dict of name -> weakness)
#         - strengths (dict of name -> strength)
#     """
#     # Extract the answer
#     answer_match = re.search(r"\{\+\{(.*?)\}\+\}", text)
#     if not answer_match:
#         raise ValueError("Missing answer block")
#     answer = answer_match.group(1).strip()

#     # Extract weaknesses block and parse pairs
#     weaknesses = {}
#     weakness_block = re.search(r"\[\+\[(.*?)\]\+\]", text)
#     if weakness_block:
#         weaknesses = dict(re.findall(r"\(\+\((.*?)<-->(.*?)\)\+\)", weakness_block.group(1)))

#     # Extract strengths block and parse pairs
#     strengths = {}
#     strength_block = re.search(r"\<\+<(.*?)>\+\>", text)
#     if strength_block:
#         strengths = dict(re.findall(r"\(\+\((.*?)<-->(.*?)\)\+\)", strength_block.group(1)))

#     return answer, weaknesses, strengths



def main():
    # Example
    # text = (
    #     "{+{This is the answer}+}"
    #     "[+[(+(claud<-->Could be clearer)+) (+(gemini<-->Too short)+)]+]"
    #     "<+<(+(claud<-->Well structured)+) (+(gemini<-->Concise)+)>+>"
    # )
    #
    # ans, weak, strong = split_response(text)
    # print("Answer:", ans)
    # print("Weaknesses:", weak)
    # print("Strengths:", strong)
    from Prompt_Engineer.prompt_engineer import OptimizeRawPrompt
    user_question = input("Enter your prompt: ")

    # prompt -> optimized prompt
    first_prompt = OptimizeRawPrompt(user_question)
    dept = int(input("Enter your dept of rethinking: "))
    cur_prompts = {mml: first_prompt for mml in MML_LIST.keys()}
    jsons = []
    improvement = False
    while dept >= 0:
        names = []
        answers = []
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
            answers.append(answer)

        names_to_answers = {}
        for name in names:
            names_to_answers[name] = {name : {}}
            for name2, answer in zip(names, answers):
                if name2 != name:
                    names_to_answers[name][name2] = answer

        jsons = [{"weaknesses" : weaknesses[name],
                  "strengths" : strengths[name],
                  "names to answers" : names_to_answers[name],
                  "first prompt" : first_prompt} for name, answer in zip(names, answers)]
        
        print("JSONs:")
        for json in jsons:
            print(json)

        for mml, json in zip(MML_LIST, jsons):
            # JSON: answer, weakness, strength -> prompt to improve next iteration with new answer
            cur_prompts[mml.name] = JSON_to_prompt(json)
        improvement = True
        dept -= 1

    return jsons

if __name__ == "__main__":
    main()
