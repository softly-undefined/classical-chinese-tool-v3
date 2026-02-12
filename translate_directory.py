# This file allows you to translate a whole directory of files instead of just a single one.

import os
from tqdm import tqdm
import translate_file
import argparse

def translate_directory(directory, output_dir, aimodel, api_key=None):
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
                translate_file.translate_file(filepath, output_dir, aimodel, api_key, output_filepath_name=output_name)
            except Exception as e:
                print(f"\nError translating {filename}: {e}")

            pbar.update(1)  # Update after each file

if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Translate all .txt files in a directory."
    )
    parser.add_argument(
        "-i", "--input", dest="directory", required=True,
        help="Input directory containing .txt files to translate (e.g. to_translate/translate1)"
    )
    parser.add_argument(
        "-o", "--output", dest="output_dir", required=True,
        help="Output directory for translated files (e.g. translated/translate1)"
    )
    parser.add_argument(
        "-m", "--model", dest="aimodel", default="gpt-4o-mini-2024-07-18",
        help="AI model to use for translation (default: gpt-4o-mini-2024-07-18)"
    )
    parser.add_argument(
        "-k", "--api-key", dest="api_key", default="",
        help="API key for the AI service (if required). If not provided, the code will attempt to use environment-based auth."
    )

    args = parser.parse_args()

    translate_directory(args.directory, args.output_dir, args.aimodel, args.api_key)