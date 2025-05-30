import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv
from .helper import *


# Load environment variables from .env file
load_dotenv()

# Load configuration from parameters.json
def load_config():
    """Load configuration parameters from JSON file"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'LLMs_config.json'), 'r') as f:
            config = json.load(f)
            return config['claude']
    except FileNotFoundError:
        print("Error: parameters.json file not found!")
        exit(1)
    except KeyError:
        print("Error: 'claude' configuration not found in parameters.json!")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in parameters.json!")
        exit(1)

# Load configuration
config = load_config()

# Initialize the Anthropic client
client = Anthropic(
    api_key=os.getenv(config['api_key_env_var'])
)

def ask_claude(question, format_response=True):
    print(f"In ask_claude with prompt: {question}, format_response: {format_response}")
    # if format_response:
    #     print(f"    format_response={format_response} --> Formatting prompt for dict: {question}")
    #     question = format_prompt_for_dict(question, LLM_name='claude')
    #     print(f"    Formatted prompt: {question}")

    """Send a question to Claude and return the response"""
    try:
        if format_response:
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=500,
                tools=[{
                    "name": "provide_comparison",
                    "description": "Provide a structured comparison of models",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "answer": {"type": "string"},
                            "strengths": {
                                "type": "object",
                                "properties": {
                                    "gpt": {"type": "string"},
                                    "gemini": {"type": "string"}
                                },
                                "required": ["gpt", "gemini"]
                            },
                            "weaknesses": {
                                "type": "object",
                                "properties": {
                                    "gpt": {"type": "string"},
                                    "gemini": {"type": "string"}
                                },
                                "required": ["gpt", "gemini"]
                            }
                        },
                        "required": ["answer", "strengths", "weaknesses"]
                    }
                }],
                tool_choice={"type": "tool", "name": "provide_comparison"},
                messages=[
                    {"role": "user", "content": "Compare these models"}
                ]
            )
            response_content = response.content[0].input

        else:
            message = client.messages.create(
                model=config['model'],
                max_tokens=config['max_tokens'],
                temperature=config['temperature'],
                messages=[
                    {
                        "role": "user",
                        "content": question
                    }
                ]
            )
            response_content = message.content[0].text
        print(f"        Raw response content: {response_content}, type: {type(response_content)}")
        # if format_response:
        #     print(f"        format_response={format_response} --> Checking and validating dict: {response_content}")
        #     cleaned_response = response_content.replace('```json', '').replace('```', '').strip()
        #     print(f"        Cleaned response: {cleaned_response}")
        #     dict_answer, error_msg = parse_and_validate_response(cleaned_response, LLM_name='claude')
        #     print(f"        Parsed dict: {dict_answer}, Error message: {error_msg}")
        #     if error_msg:
        #         return f"{config['error_prefix']}: {error_msg}"
        #     print(f"        Returning dict answer: {dict_answer}")
        #     return dict_answer
        # else:
        #     return response_content
        return response_content
    except Exception as e:
        return f"{config['error_prefix']}: {str(e)}"

def main():
    print(f"Now talking with: {config['model']}")
    print(f"{config['quit_instruction']}")
    while True:
        # Get user input
        question = input(f"{config['user_prompt']}: ").strip()
        
        # Check if user wants to quit
        if question.lower() in config['quit_commands']:
            break
        
        # Skip empty questions
        if not question:
            continue
        
        # Get response from Claude
        print(f"{config['assistant_name']}: ", end="")
        response = ask_claude(question)
        print(response)
        print(config['separator'] * config['separator_length'])

if __name__ == "__main__":
    main()