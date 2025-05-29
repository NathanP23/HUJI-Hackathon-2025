import os
import json
from dotenv import load_dotenv
import openai
from openai import OpenAI



# Load environment variables from .env file
load_dotenv()

# Load configuration from parameters.json
def load_config():
    """Load configuration parameters from JSON file"""
    try:
        with open('LLMs_config.json', 'r') as f:
            config = json.load(f)
            return config['gpt']
    except FileNotFoundError:
        print("Error: parameters.json file not found!")
        exit(1)
    except KeyError:
        print("Error: 'gpt' configuration not found in parameters.json!")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in parameters.json!")
        exit(1)

# Load configuration
config = load_config()

# Get API key from environment
api_key = os.getenv(config['api_key_env_var'])
if not api_key:
    raise ValueError(f"{config['api_key_env_var']} not found in .env file")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def ask_gpt(prompt, model=None):
    """Send a prompt to GPT and return the response"""
    if model is None:
        model = config['model']
    
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": config['system_message']},
                {"role": "user", "content": prompt},
            ],
            temperature=config['temperature'],
            max_tokens=config['max_tokens']
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"{config['error_prefix']}: {e}"

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
        
        # Get response from GPT
        print(f"{config['assistant_name']}: ", end="")
        answer = ask_gpt(question)
        print(answer)
        print(config['separator'] * config['separator_length'])

if __name__ == "__main__":
    main()
