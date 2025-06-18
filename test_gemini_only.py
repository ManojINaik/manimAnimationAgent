import os
from dotenv import load_dotenv
import google.generativeai as genai
import random

load_dotenv()

gemini_key_env = os.getenv('GEMINI_API_KEY')
if ',' in gemini_key_env:
    keys = [key.strip() for key in gemini_key_env.split(',') if key.strip()]
    api_key = random.choice(keys)
    print(f"Selected random key: {api_key[:20]}...")
else:
    api_key = gemini_key_env
    print(f"Using single key: {api_key[:20]}...")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro')
response = model.generate_content('Say hello in one word')
print(f'Success! Response: {response.text.strip()}') 