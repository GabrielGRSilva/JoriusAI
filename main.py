import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv(".env") #loads environment variables from gemkey.env file
api_key = os.environ.get("GEMINI_API_KEY") #reads gemini API key

client = genai.Client(api_key=api_key) #creates new instance of Gemini client

if len(sys.argv) < 2:         #checks if a prompt is provided as a command line argument
    print("ERROR: Please provide a prompt as a command line argument.")
    sys.exit(1)


user_prompt = sys.argv[1]

messages = [
types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

test_generation = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=messages)
print(test_generation.text)

if "--verbose" in sys.argv:
    print(f"User prompt: {user_prompt}",'\n'
    f'Prompt tokens: {test_generation.usage_metadata.prompt_token_count}', '\n'
    f'Response tokens: {test_generation.usage_metadata.candidates_token_count}')
