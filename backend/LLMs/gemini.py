import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load configuration from parameters.json
def load_config():
    """Load configuration parameters from JSON file"""
    try:
        with open('LLMs_config.json', 'r') as f:
            config = json.load(f)
            return config['gemini']
    except FileNotFoundError:
        print("Error: parameters.json file not found!")
        exit(1)
    except KeyError:
        print("Error: 'gemini' configuration not found in parameters.json!")
        exit(1)
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in parameters.json!")
        exit(1)

# Load configuration
config = load_config()

# Get API key from environment
api_key = os.getenv(config['api_key_env_var'])
if not api_key:
    print(f"{config['error_prefix']}: '{config['api_key_env_var']}' not found in environment variables or .env file.")
    print(config['api_key_setup_instruction'])
    print(config['api_key_url_instruction'])
    exit(1)

# Initialize Gemini client
genai.configure(api_key=api_key)
model = genai.GenerativeModel(config['model'])

def ask_gemini(prompt):
    """Send a prompt to Gemini and return the response"""
    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=config['temperature'],
                max_output_tokens=config['max_tokens']
            )
        )
        return response.text
    except Exception as e:
        return f"{config['error_prefix']}: {e}. {config['error_suggestion']}"

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
        
        # Get response from Gemini
        print(f"{config['assistant_name']}: ", end="")
        answer = ask_gemini(question)
        print(answer, end="")
        print(config['separator'] * config['separator_length'])

if __name__ == "__main__":
    # Check if interactive mode is enabled
    if config.get('interactive_mode', True):
        main()
    else:
        # Single question mode
        question = input(f"{config['single_question_prompt']}: ")
        answer = ask_gemini(question)
        print(f"{config['response_prefix']}: {answer}")