import os

def write_file(working_directory, file_path, content):
    if not os.path.isabs(file_path):
        file_path = os.path.join(working_directory, file_path)

    abs_path_file = os.path.abspath(file_path)
    abs_path_working_directory = os.path.abspath(working_directory)
    
        
        #Security check to prevent agent acessing files outside the working directory:

    if not (abs_path_file.startswith(abs_path_working_directory + os.sep) or abs_path_file == abs_path_working_directory): 
        return(f'Error: Cannot write "{file_path}" as it is outside the permitted working directory')

    try:
        with open(abs_path_file, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as e:
        return f'Error: {e} for file {file_path} (maybe file already exists?)'