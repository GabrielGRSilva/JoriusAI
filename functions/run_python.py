import os
import subprocess

def run_python_file(working_directory, file_path):
    complete_file_path = os.path.join(working_directory, file_path)

    abs_file_path = os.path.abspath(complete_file_path)
    abs_path_working_directory = os.path.abspath(working_directory)

    #Security check to prevent agent acessing files outside the working directory:

    if not (abs_file_path.startswith(abs_path_working_directory + os.sep) or abs_file_path == abs_path_working_directory): 
        return(f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory')
    elif not os.path.isfile(file_path):
        return(f'Error: File "{file_path}" not found.')
    elif not file_path.endswith('.py'):
        return(f'Error: "{file_path}" is not a Python file')
    
    try:
        run_results = subprocess.run(['python', abs_file_path], timeout=30, cwd=abs_path_working_directory, capture_output=True)
        result_stdout = run_results.stdout.decode('utf-8').strip()
        result_stderr = run_results.stderr.decode('utf-8').strip()
        code = run_results.returncode
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
    output = ''
    if result_stdout and result_stderr:
        output = f'STDOUT: {result_stdout} \n STDERR: {result_stderr} \n'
    elif result_stdout:
        output = f'STDOUT: {result_stdout} \n'
    elif result_stderr:
        output = f'STDERR: {result_stderr} \n'
        
    if code != 0:
        output += f'Process exited with code {code}'
    
    if output:
        return output
    else:
        return 'No output produced.'