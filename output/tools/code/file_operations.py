"""
Perform basic file operations (read, write, list).
"""

import os
from pathlib import Path

def file_operations(operation: str, filename: str, content: str = "") -> str:
    """
    Perform basic file operations (read, write, list).
    
    Args:
        operation: Operation type ("read", "write", "list", "exists")
        filename: File path (relative to output directory)
        content: Content to write (for write operation)
    
    Returns:
        Result of the file operation
    """
    try:
        base_dir = Path("output/temp")
        base_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = base_dir / filename
        
        # Security check - ensure file is within base directory
        if not str(file_path.resolve()).startswith(str(base_dir.resolve())):
            return "Error: File path not allowed for security reasons"
        
        if operation == "read":
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                return f"Content of {filename}:\n{file_content}"
            else:
                return f"Error: File {filename} does not exist"
                
        elif operation == "write":
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return f"Successfully wrote to {filename}"
            
        elif operation == "list":
            files = [f.name for f in base_dir.iterdir() if f.is_file()]
            return f"Files in directory:\n" + "\n".join(files) if files else "No files found"
            
        elif operation == "exists":
            exists = file_path.exists()
            return f"File {filename} {'exists' if exists else 'does not exist'}"
            
        else:
            return f"Error: Unknown operation '{operation}'. Use: read, write, list, exists"
            
    except Exception as e:
        return f"File operation error: {str(e)}"
