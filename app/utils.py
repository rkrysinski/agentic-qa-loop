import chainlit as cl

"""
Utility functions for file processing.
"""

def extract_text_from_file(file) -> str:
    """
    Extract text content from a file.
    
    Args:
        file: Either a file object with .path attribute or a string path
    
    Returns:
        Text content of the file
    """
    # Handle both file objects (with .path) and string paths
    file_path = file.path if hasattr(file, 'path') else file
    
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()
