import os

def load_instruction_from_file(filename: str) -> str:
    """
    Load and return the contents of a text file.

    The function resolves `filename` relative to the directory of this script.
    If an absolute path is provided, it is used as-is.

    Parameters
    ----------
    filename : str
        Name of the instruction file or an absolute file path.

    Returns
    -------
    str
        The full text content of the file.

    Raises
    ------
    FileNotFoundError
        If the file cannot be found.
    IOError
        If the file cannot be read.
    """
    # If user supplies absolute path, trust it
    if os.path.isabs(filename):
        file_path = filename
    else:
        # Resolve relative to this script's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(current_dir, filename)

    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"Instruction file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()