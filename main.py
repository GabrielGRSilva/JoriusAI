import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
#Maybe organize this later into a single file to import them at once?
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.run_python_file import run_python_file
from functions.write_file import write_file



load_dotenv(".env") #loads environment variables from gemkey.env file
api_key = os.environ.get("GEMINI_API_KEY") #reads gemini API key
client = genai.Client(api_key=api_key) #creates new instance of Gemini client

if len(sys.argv) < 2:         #checks if a prompt is provided as a command line argument
    print("ERROR: Please provide a prompt as a command line argument.")
    sys.exit(1)

####Function Calls

function_dic = {        #This dictionary maps available function names to their respective functions.
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file}

def call_function(function_call_part, verbose=False):
    if function_call_part.name not in function_dic:
        return types.Content(role="tool", parts=[types.Part.from_function_response(name=function_call_part.name, 
        response={"error": f"Unknown function: {function_call_part.name}"},)],)
    
    if verbose == True:
        print(f"- Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f"- Calling function: {function_call_part.name}")

    dir_and_args = {**function_call_part.args, "working_directory": "./calculator"} #adds the working directory to the function call arguments

    function_result = function_dic[function_call_part.name](**dir_and_args) #calls the function with the provided arguments
    return types.Content(
    role="tool",
    parts=[
        types.Part.from_function_response(
            name=function_call_part.name,
            response={"result": function_result},)],)

#Function Call Schemes

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
###
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the content of an specific file in the specified path if the path is in the working directory. Limited to 10001 characters, otherwise it will truncate the result.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file_path where the file is, relative to the working directory.",
            ),
        },
    ),
)
###
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="If the file_path points to a Python file, it will execute the file and return the output. If the file_path is not a Python file or is outside the working directory, it will return an error message.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file_path where the file is, relative to the working directory."),

            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Arguments to pass to the python file.",
            ),}
            ),
    )
####
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Create a file and write the contents of the variable content to it. If the file already exists, return an error message. If the file_path is outside the working directory, it will return an error message.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file_path where the file should be written."
            ),
             "content": types.Schema(
                type=types.Type.STRING,
                description="The content that should be written to the file.",
            ),
        },
    ),
)
####

available_functions = types.Tool(function_declarations=[schema_get_files_info, schema_get_file_content, schema_run_python_file, schema_write_file])

###The System Prompt is like a briefing to the AI, telling him what he is and what to do

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory.

You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""
user_prompt = sys.argv[1]

messages = [
types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=messages,
    config=types.GenerateContentConfig(
    tools=[available_functions], system_instruction=system_prompt,
    ))



loop_count = 0

while loop_count < 20: #this limits how many times the AI can loop
    function_called = False
    for candidate in response.candidates:
        messages.append(candidate.content)

        if candidate.content:
            for part in candidate.content.parts:
                if part.function_call:
                    function_called = True

                    loop_count += 1
                
                    if "--verbose" in sys.argv:
                        execute_function = call_function(part.function_call, verbose=True)
                    else:
                        execute_function = call_function(part.function_call)

                    if not execute_function.parts[0].function_response.response:
                        raise Exception(f"FATAL ERROR: Function {part.function_call.name} did not return a response.")
                    
                    messages.append(execute_function)

                    response = client.models.generate_content(
                        model='gemini-2.0-flash-001',
                        contents=messages,
                        config=types.GenerateContentConfig(
                        tools=[available_functions], system_instruction=system_prompt,
                        ))
            
    if function_called == False:
        print(f'Final response:\n{response.text}') #This is the final answer from the AI after executing all the function calls.
        break