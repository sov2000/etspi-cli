import os
import glob
import shutil  # For secure file deletion (avoids potential issues with os.remove)

def delete_files_with_extensions(root_folder, extensions):
    """
    Searches for files with specified extensions in all subfolders of a root folder
    and deletes them.

    Args:
        root_folder: The path to the root folder to search.
        extensions: A list of file extensions (e.g., [".txt", ".log", ".bak"]).
                    Can also include wildcards like ["*.txt", "*.log"].
    """

    for ext in extensions: # loop over the extensions
        files_to_delete = glob.glob(os.path.join(root_folder, "**", ext), recursive=True) # find files recursively

        if files_to_delete: # if there are any files found with that extension
            print(f"Found {len(files_to_delete)} files with extension {ext} to delete.")
            for file_path in files_to_delete:
                try:
                    # Use shutil.move() to move to trash or a temporary directory (safer than direct deletion)
                    # For actual deletion (irreversible), replace with:
                    # os.remove(file_path)

                    trash_dir = os.path.join(root_folder, ".trash") # Example trash directory
                    if not os.path.exists(trash_dir):
                        os.makedirs(trash_dir)

                    base_name = os.path.basename(file_path)
                    new_path = os.path.join(trash_dir, base_name) # Move to trash

                    shutil.move(file_path, new_path) # Move to trash

                    print(f"Moved {file_path} to trash: {new_path}")


                    # If you are sure you want to delete directly and NOT move to trash, uncomment the following line and comment out the move to trash code:
                    # os.remove(file_path)
                    # print(f"Deleted {file_path}")

                except Exception as e:
                    print(f"Error deleting/moving {file_path}: {e}")
        else:
            print(f"No files with extension {ext} found.")

# Example with only wildcards

root_directory2 = "./test_files"
file_extensions2 = ["*.etjs", "*.etyml", "*.ejs", "*.eyml"]

delete_files_with_extensions(root_directory2, file_extensions2)