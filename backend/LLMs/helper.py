
import ast

def format_prompt_for_dict(prompt, LLM_name):
    LLM_names = list({'gpt', 'claude', 'gemini'} - {LLM_name})
    """Add dictionary format instructions to the prompt"""
    format_instruction = (f"Answer the following prompt ONLY in the following format as a dictionary, please keep track of all parantheses and symbols required!:"
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
    return format_instruction + prompt

def validate_dict_structure(dict_answer, LLM_name):
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

    """Parse response as dictionary and validate its structure"""
    try:
        dict_answer = ast.literal_eval(response_content)
        is_valid, error_msg = validate_dict_structure(dict_answer, LLM_name=LLM_name)
        
        if not is_valid:
            return None, error_msg
        
        return dict_answer, None
        
    except (ValueError, SyntaxError) as e:
        return None, f"Invalid dictionary format: {e}"

def JSON_to_prompt(json_dict):
    """Convert a dictionary to a prompt string"""
    if not isinstance(json_dict, dict):
        raise ValueError("Input must be a dictionary")
    
    prompt = ""
    for key, value in json_dict.items():
        if isinstance(value, dict):
            value_str = ", ".join(f"{k}: {v}" for k, v in value.items())
            prompt += f"{key}:\n{{{value_str}}}\n"
        else:
            prompt += f"{key}: {value}\n"
    
    return prompt.strip()