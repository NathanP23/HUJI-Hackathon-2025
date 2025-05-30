
import ast

def format_prompt_for_dict(prompt, LLM_name):
    print(f"        Inside format_prompt_for_dict, Formatting prompt for dictionary structure for {LLM_name}")
    LLM_names = list({'gpt', 'claude', 'gemini'} - {LLM_name})
    print(f"        LLM_names: {LLM_names}")
    """Add dictionary format instructions to the prompt"""
    format_instruction = (f"Answer the following prompt ONLY in the following format (as a JSON only), please keep track of all parantheses and symbols required!:"
                         "{"
                         "    'answer': 'answer to the prompt',"
                         "    'strengths': {"
                         "        '"+LLM_names[0]+"': 'strength of the "+LLM_names[0]+" answer',"
                         "        '"+LLM_names[1]+"': 'strength of the "+LLM_names[1]+" answer'"
                         "    },"
                         "    'weaknesses': {"
                         "        '"+LLM_names[0]+"': 'weakness of the "+LLM_names[0]+" answer',"
                         "        '"+LLM_names[1]+"': 'weakness of the "+LLM_names[1]+" answer'"
                         "    }"
                         "}")
    print(f"        format_instruction prompt is: {format_instruction}")
    print(f"        format_instruction + prompt.")
    return format_instruction + prompt

def validate_dict_structure(dict_answer, LLM_name):
    print(f"        Inside validate_dict_structure, Validating dictionary structure for {LLM_name}")
    """Validate that the dictionary has the expected structure"""
    if not isinstance(dict_answer, dict):
        return False, "Response is not a dictionary"
    
    # Check required keys
    required_keys = {'answer', 'strengths', 'weaknesses'}
    if not required_keys.issubset(dict_answer.keys()):
        return False, "Missing required keys"
    
    # Check that strengths and weaknesses are dicts with claude/gemini keys
    for key in ['strengths', 'weaknesses']:
        if not isinstance(dict_answer[key], dict):
            return False, f"{key} must be a dictionary"
        LLM_names = list({'gpt', 'claude', 'gemini'} - {LLM_name})
        if not {LLM_names[0], LLM_names[1]}.issubset(dict_answer[key].keys()):
            return False, f"{key} missing {LLM_names[0]}/{LLM_names[1]}"
    
    return True, "Valid"

def parse_and_validate_response(response_content, LLM_name):
    print(f"        Inside parse_and_validate_response, Parsing response content for {LLM_name}")
    """Parse response as dictionary and validate its structure"""
    try:
        dict_answer = ast.literal_eval(response_content)
        print(f"        Parsed dictionary: {dict_answer}")
        is_valid, error_msg = validate_dict_structure(dict_answer, LLM_name=LLM_name)
        print(f"        Validation result: {is_valid}, Error message: {error_msg}")

        if not is_valid:
            return None, error_msg
        
        return dict_answer, None
        
    except (ValueError, SyntaxError) as e:
        return None, f"Invalid dictionary format: {e}"


def generate_improvement_prompt(data: dict) -> str:
    """
    Given a dict with keys:
      - "original_question": str
      - "old answer": str
      - "strengths": List[str]
      - "weaknesses": List[str]
      - "names to answers": Dict[str, str]
    returns a single prompt string to:
      1) Critique each AI answer
      2) Improve the old answer
    """
    # Extract fields
    question    = data.get("original_question", "").strip()
    old_answer  = data.get("old answer", "").strip()
    strengths   = data.get("strengths", [])
    weaknesses  = data.get("weaknesses", [])
    names_ans   = data.get("names to answers", {})

    # Build prompt parts
    parts = []

    # 1. Original question
    parts.append(f"Original question:\n{question}\n")

    # 2. Aggregated strengths & weaknesses
    if strengths:
        parts.append("Aggregated strengths:\n" +
                     "\n".join(f"- {s}" for s in strengths) + "\n")
    if weaknesses:
        parts.append("Aggregated weaknesses:\n" +
                     "\n".join(f"- {w}" for w in weaknesses) + "\n")

    # 3. Critique each AI answer
    parts.append("For each of the following AI-generated answers, provide a concise, honest, and assertive critique, highlighting what works, what doesn't, and how it could be improved:\n")
    for name, answer in names_ans.items():
        parts.append(f"---\nAnswer by {name}:\n{answer}\n")

    # 4. Improve the old answer
    parts.append(
        "\n---\n"
        "Now, taking into account the critiques above, please rewrite and improve the previous answer below:\n"
        f"{old_answer}\n"
    )

    # Join all parts into one prompt string
    return "\n".join(parts)
