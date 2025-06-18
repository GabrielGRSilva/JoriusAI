import os

def get_files_info(working_directory, directory=None):
    if directory is None:
        directory = working_directory  # Default to the working directory if no directory is specified
    
    if not os.path.isabs(directory):
        directory = os.path.join(working_directory, directory)

    abs_path_directory = os.path.abspath(directory)
    abs_path_working_directory = os.path.abspath(working_directory)

    #Security check to prevent agent acessing files outside the working directory:

    if not (abs_path_directory.startswith(abs_path_working_directory + os.sep) or abs_path_directory == abs_path_working_directory): 
        return(f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
    elif not os.path.isdir(directory):
        return(f'Error: "{directory}" is not a directory')

    
    contents = os.listdir(directory)

    information_list = []
    for file in contents:
        try:
            file_size = os.path.getsize(os.path.join(directory, file))
            is_dir = os.path.isdir(os.path.join(directory, file))

            information_list.append(f'- {file}: file_size={file_size} bytes, is_dir={is_dir}')
        except Exception as e:
            information_list.append(f'Error: {e} for file {file}')

    return '\n'.join(information_list) if information_list else f'No files found in {directory}'
        
        