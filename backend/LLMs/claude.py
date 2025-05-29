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
    if format_response:
        question = format_prompt_for_dict(question, LLM_name='claude')
    """Send a question to Claude and return the response"""
    try:
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
        if format_response:
            cleaned_response = response_content.replace('```json', '').replace('```', '').strip()
            dict_answer, error_msg = parse_and_validate_response(cleaned_response, LLM_name='claude')
            if error_msg:
                return f"{config['error_prefix']}: {error_msg}"
            return dict_answer
        else:
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