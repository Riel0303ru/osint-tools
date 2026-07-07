from pathlib import Path

def generate_tree(dir_path: Path, prefix: str = "", ignore_list: set = None):
    if ignore_list is None:
        ignore_list = {'venv', '.git', '__pycache__'}

    try:
        items = sorted(dir_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        return

    items = [item for item in items if item.name not in ignore_list]

    for index, item in enumerate(items):
        is_last = index == len(items) - 1
        connector = "└── " if is_last else "├── "
        
        print(f"{prefix}{connector}{item.name}")
        
        if item.is_dir():
            extension = "    " if is_last else "│   "
            generate_tree(item, prefix=prefix + extension, ignore_list=ignore_list)

if __name__ == "__main__":
    target_directory = Path(".") 
    
    print(f"Struktur folder dari: {target_directory.resolve()}\n")
    generate_tree(target_directory)