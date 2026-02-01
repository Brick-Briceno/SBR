import os
import sys
import re
from pathlib import Path

def count_lines_in_file(file_path):
    """Count lines in a file, handling UTF-8 encoding."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except (UnicodeDecodeError, PermissionError, OSError) as e:
        # Skip binary files or files that can't be read
        return 0

def get_file_extension(file_path):
    """Get file extension in lowercase, or 'no_extension' if none."""
    ext = os.path.splitext(file_path)[1].lower()
    return ext if ext else 'no_extension'

def parse_gitignore(root_dir):
    """Parse .gitignore file and return a list of patterns to ignore."""
    gitignore_path = os.path.join(root_dir, '.gitignore')
    ignore_patterns = []
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                # Remove trailing slash for directories
                if line.endswith('/'):
                    line = line[:-1]
                ignore_patterns.append(line)
    
    return ignore_patterns

def should_ignore(path, ignore_patterns, root_dir):
    """Check if a path should be ignored based on .gitignore patterns."""
    rel_path = os.path.relpath(path, root_dir).replace('\\', '/')
    
    # Always ignore .git directory
    if '.git' in rel_path.split(os.sep):
        return True
        
    for pattern in ignore_patterns:
        # Handle directory patterns (ending with /)
        if pattern.endswith('/'):
            pattern = pattern[:-1]
            if pattern in rel_path.split('/'):
                return True
        # Handle file patterns
        elif pattern in rel_path.split('/')[-1]:
            return True
        # Handle patterns with wildcards
        elif '*' in pattern:
            # Convert gitignore pattern to regex
            regex = pattern.replace('.', '\.').replace('*', '.*')
            if re.search(regex, rel_path):
                return True
    return False

def scan_repository(root_dir):
    """Scan repository and count lines in all files."""
    line_counts = {}
    total_lines = 0
    file_count = 0
    
    # Common directories to skip
    skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'build', 'dist'}
    
    # Get .gitignore patterns
    ignore_patterns = parse_gitignore(root_dir)
    
    print(f"Scanning directory: {root_dir}\n")
    
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # Skip unwanted directories and those matching .gitignore
        dirs[:] = [d for d in dirs 
                  if (d not in skip_dirs and 
                      not should_ignore(os.path.join(root, d), ignore_patterns, root_dir))]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Skip hidden files and files matching .gitignore
            if (file.startswith('.') or 
                should_ignore(file_path, ignore_patterns, root_dir)):
                continue
                
            ext = get_file_extension(file)
            lines = count_lines_in_file(file_path)
            
            if lines > 0:  # Only count files we could read
                rel_path = os.path.relpath(file_path, root_dir)
                line_counts[ext] = line_counts.get(ext, 0) + lines
                print(f"{rel_path}: {lines} lines")
                total_lines += lines
                file_count += 1
    
    return line_counts, total_lines, file_count

def main():
    # Get repository root (current directory by default)
    repo_root = os.getcwd()
    
    # If a path is provided as argument, use it
    if len(sys.argv) > 1:
        repo_root = os.path.abspath(sys.argv[1])

    if not os.path.exists(repo_root):
        print(f"Error: Directory not found: {repo_root}")
        sys.exit(1)

    line_counts, total_lines, file_count = scan_repository(repo_root)

    print("\n" + "="*50)
    print("LINE COUNT SUMMARY")
    print("="*50)

    # Print counts by file extension
    for ext, count in sorted(line_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"{ext or 'no_extension'}: {count} lines")
    
    print("-"*50)
    print(f"Total files: {file_count}")
    print(f"Total lines: {total_lines}")
    print("="*50)

if __name__ == "__main__":
    main()
