import yaml
import sys

def redirect_print_to_log(log_file_path, mode="w"):
    """
    Redirect all print() output to the given log file.
    
    Args:
        log_file_path (str): Path to the log file.
        mode (str): File mode, "a" for append or "w" for overwrite.
    """
    log_file = open(log_file_path, mode)
    sys.stdout = log_file
    sys.stderr = log_file  # Redirect errors as well
    print(f"[Logger] Redirected stdout/stderr to {log_file_path}")

def read_file(path):
    with open(path, "r") as f:
        if path.endswith("yaml"):
            data = yaml.safe_load(f)
        else:
            data = f.read()
    return data