import os

def get_file_content(working_directory, file_path):
    if not os.path.isabs(file_path):
        file_path = os.path.join(working_directory, file_path)

    abs_path_file = os.path.abspath(file_path)
    abs_path_working_directory = os.path.abspath(working_directory)
    
    #Security check to prevent agent acessing files outside the working directory:

    if not (abs_path_file.startswith(abs_path_working_directory + os.sep) or abs_path_file == abs_path_working_directory): 
        return(f'Error: Cannot read "{file_path}" as it is outside the permitted working directory')
    elif not os.path.isfile(abs_path_file):
        return(f'Error: File not found or is not a regular file: "{file_path}"')
    
    try:
        with open(abs_path_file, "r") as f:
            content = f.read(10001) # Read up to 10001 characters
    
        if len(content) > 10000:
            content = content[:10000] + f'[...File "{file_path}" truncated at 10000 characters]'
        
        return content
    except Exception as e:
        return f'Error: {e} for file {file_path}'
    
