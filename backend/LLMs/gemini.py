import os
import json
import google.generativeai as genai
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

def ask_gemini(prompt, format_response=True):
    print(f"In ask_gemini with prompt: {prompt}, format_response: {format_response}")
    """Send a prompt to Gemini and return the response"""
    try:
        if format_response:

            # Define the schema
            response_schema = {
                "type": "object",
                "properties": {
                    "answer": {"type": "string"},
                    "strengths": {
                        "type": "object",
                        "properties": {
                            "gpt": {"type": "string"},
                            "claude": {"type": "string"}
                        },
                        "required": ["gpt", "claude"]
                    },
                    "weaknesses": {
                        "type": "object",
                        "properties": {
                            "gpt": {"type": "string"},
                            "claude": {"type": "string"}
                        },
                        "required": ["gpt", "claude"]
                    }
                },
                "required": ["answer", "strengths", "weaknesses"]
            }

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                    response_schema=response_schema
                )
            )

            response = model.generate_content("Compare these two answers and their performance",)
            response_content = json.loads(response.text)
        else:
            response = model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=config['temperature'],
                    max_output_tokens=config['max_tokens']
                )
            )
            response_content = response.text
        print(f"        Raw response content: {response_content}, type: {type(response_content)}")
        return response_content
    except Exception as e:
        return f"{config['error_prefix']}: {e}."

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
    main()
