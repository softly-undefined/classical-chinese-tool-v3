# This file allows you to translate a whole directory of files instead of just a single one.

import os
from tqdm import tqdm
import translate_file

def translate_directory(directory, output_dir, aimodel):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Collect all .txt files in the directory
    txt_files = [
        f for f in os.listdir(directory)
        if os.path.isfile(os.path.join(directory, f)) and f.lower().endswith(".txt")
    ]

    # Use tqdm to show progress
    with tqdm(total=len(txt_files), desc="Translating files", unit="file") as pbar:
        for filename in txt_files:
            filepath = os.path.join(directory, filename)
            base_name = os.path.splitext(filename)[0]
            output_name = f"{base_name}_translated"

            try:
                translate_file.translate_file(filepath, output_dir, aimodel, output_filepath_name=output_name)
            except Exception as e:
                print(f"\nError translating {filename}: {e}")

            pbar.update(1)  # Update after each file

if __name__ == "__main__":
    DIRECTORY = "DIRECTORY_TO_TRANSLATE"
    OUTPUT_DIR = "DIRECTORY_FOR_TRANSLATED_FILES"
    AI_MODEL = "CHOSEN_MODEL_NAME" # TODO: Rewrite translation models system to work better with the system?
    translate_directory(DIRECTORY, OUTPUT_DIR, AI_MODEL)