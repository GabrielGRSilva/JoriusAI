import os
import sys
from dotenv import load_dotenv
from google import genai

load_dotenv(".env") #loads environment variables from gemkey.env file
api_key = os.environ.get("GEMINI_API_KEY") #reads gemini API key

client = genai.Client(api_key=api_key) #creates new instance of Gemini client

try:
    test_generation = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=[sys.argv[1]])
    print(test_generation.text, '\n', f'Prompt tokens: {test_generation.usage_metadata.prompt_token_count}', '\n', f'Response tokens: {test_generation.usage_metadata.candidates_token_count}')

except:
    print("ERROR: Please provide a prompt as a command line argument.")
    sys.exit(1)