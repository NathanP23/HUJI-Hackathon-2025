import os
import json
from anthropic import Anthropic
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from parameters.json
def load_config():
    """Load configuration parameters from JSON file"""
    try:
        with open('LLMs_config.json', 'r') as f:
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

def ask_claude(question):
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
        return message.content[0].text
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