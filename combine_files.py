import os

def collect_files(root_dir, output_file):
    # Supported extensions
    extensions = ['.py', '.json', '.txt']
    # Folders to skip
    skip_folders = {'__pycache__', '.pytest_cache', 'venv', '.git'}

    with open(output_file, 'w', encoding='utf-8') as outfile:
        for foldername, subfolders, filenames in os.walk(root_dir):
            # Modify subfolders in-place to skip unwanted ones
            subfolders[:] = [d for d in subfolders if d not in skip_folders]

            for filename in filenames:
                _, ext = os.path.splitext(filename)
                if ext.lower() in extensions:
                    file_path = os.path.join(foldername, filename)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                    except Exception as e:
                        content = f"Error reading file: {e}"

                    # Write file header and content
                    outfile.write(f"# ==== {file_path} ====\n")
                    outfile.write(content + "\n\n")

    print(f"✅ All files have been written to {output_file}")


if __name__ == "__main__":
    # Change this to your root folder if needed
    root_directory = "."
    output_filename = "combined_output.txt"
    collect_files(root_directory, output_filename)
