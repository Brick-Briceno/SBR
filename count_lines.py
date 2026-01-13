import os
import sys

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

def scan_repository(root_dir):
    """Scan repository and count lines in all files."""
    line_counts = {}
    total_lines = 0
    file_count = 0
    
    # Skip common directories that shouldn't be counted
    skip_dirs = {'.git', '__pycache__', 'node_modules', 'venv', '.venv', 'build', 'dist'}
    
    print(f"Scanning directory: {root_dir}\n")
    
    for root, dirs, files in os.walk(root_dir):
        # Skip unwanted directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, root_dir)
            
            # Skip hidden files
            if file.startswith('.'):
                continue
                
            ext = get_file_extension(file)
            lines = count_lines_in_file(file_path)
            
            if lines > 0:  # Only count files we could read
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
