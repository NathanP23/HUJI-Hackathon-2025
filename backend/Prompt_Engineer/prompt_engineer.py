import os
import json
from dotenv import load_dotenv
from openai import OpenAI

def load_json(path, key=None):
    """Load entire JSON or return sub-key if given."""
    with open(path, 'r') as f:
        data = json.load(f)
    return data[key] if key else data

# load env & API config
load_dotenv()
config = load_json('prompt_engineer_config.json')['prompt_engineer']
client = OpenAI(api_key=os.getenv(config['api_key_env_var']))
if not client.api_key:
    print(f"Error: Environment variable {config['api_key_env_var']} not set.")
    exit(1)

# load our static config
cfg = load_json('prompt_engineer_config.json')

def ask_llm(messages):
    resp = client.chat.completions.create(
        model=config['model'],
        messages=messages,
        temperature=config['temperature'],
        max_tokens=config['max_tokens']
    )
    return resp.choices[0].message.content.strip()

def classify_prompt(user_prompt):
    sys_msg = cfg['classification']['system_prompt']
    examples = cfg['classification']['examples']
    messages = [{"role": "system", "content": sys_msg}]
    for ex in examples:
        messages.append({"role": "user",    "content": ex['prompt']})
        messages.append({"role": "assistant","content": ex['category']})
    messages.append({"role": "user", "content": user_prompt})
    category = ask_llm(messages).lower()

    # override rules
    for cat, keywords in cfg['classification']['override_keywords'].items():
        if any(kw in user_prompt.lower() for kw in keywords):
            category = cat
            break
    return category

def select_strategy(category):
    return cfg['strategies'].get(category, cfg['strategies']['default'])

def optimize_prompt(original, category, strategy):
    base = cfg['optimization']['base_system'].format(strategy=strategy)
    extra = cfg['optimization']['extras'].get(category, "")
    system = base + extra

    messages = [
        {"role": "system", "content": system},
        {"role": "user",   "content": original}
    ]
    return ask_llm(messages)

def main():
    print(f"Now talking with - Prompt engineer: {config['model']}")
    print(f"{config['quit_instruction']}")
    while True:
        user_prompt = input(f"{config['user_prompt']}: ").strip()

        if not user_prompt: continue
        if user_prompt.lower() in ('exit', 'quit'):
            break

        category = classify_prompt(user_prompt)
        print(f"\n[Classification] {category}")

        strategy = select_strategy(category)
        print(f"[Strategy] {strategy}")

        optimized = optimize_prompt(user_prompt, category, strategy)
        print("\n🔄 Optimized Prompt:")
        print(optimized)
        print("—" * 40)

if __name__ == "__main__":
    main()
