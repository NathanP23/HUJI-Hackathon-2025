import os
import json
from dotenv import load_dotenv
from openai import OpenAI
from .helper import *



# Load environment variables from .env file
load_dotenv()

# Load configuration from parameters.json
def load_config():
    """Load configuration parameters from JSON file"""
    try:
        with open(os.path.join(os.path.dirname(__file__), 'LLMs_config.json'), 'r') as f:
            config = json.load(f)
            return config['gpt']
    except FileNotFoundError:
        print("Error: LLMs_config.json file not found!")
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

def ask_gpt(prompt, format_response=True):
    print(f"In ask_gpt with prompt: {prompt}, format_response: {format_response}")
    """Send a prompt to GPT and return the response"""
    try:
        if format_response:
            response = client.chat.completions.create(
                max_tokens=500,
                model="gpt-4o",  # Must use gpt-4o or gpt-4o-mini for structured outputs
                messages=[
                    {"role": "user", "content": "Provide a structured comparison of answers of those two models"}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "model_comparison",
                        "strict": True,  # Enforces exact schema compliance
                        "schema": {
                            "type": "object",
                            "properties": {
                                "answer": {"type": "string"},
                                "strengths": {
                                    "type": "object",
                                    "properties": {
                                        "claude": {"type": "string"},
                                        "gemini": {"type": "string"}
                                    },
                                    "required": ["claude", "gemini"],
                                    "additionalProperties": False
                                },
                                "weaknesses": {
                                    "type": "object",
                                    "properties": {
                                        "claude": {"type": "string"},
                                        "gemini": {"type": "string"}
                                    },
                                    "required": ["claude", "gemini"],
                                    "additionalProperties": False
                                }
                            },
                            "required": ["answer", "strengths", "weaknesses"],
                            "additionalProperties": False
                        }
                    }
                }
            )
            response_content = json.loads(response.choices[0].message.content)
        else:
            response = client.chat.completions.create(
                model=config['model'],
                messages=[
                    {"role": "system", "content": config['system_message']},
                    {"role": "user", "content": prompt},
                ],
                temperature=config['temperature'],
                max_tokens=config['max_tokens']
            )
            response_content = response.choices[0].message.content.strip()
        print(f"        Raw response content: {response_content}, type: {type(response_content)}")
        return response_content
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
