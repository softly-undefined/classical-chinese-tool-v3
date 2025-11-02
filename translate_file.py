# This file will take in a file, and return a super long string with markers throughout.
# TODO: Add a translation harness system to avoid "The translation is..." etc. in outputs.
# Use this for that ^ https://github.com/wmt-conference/wmt-collect-translations
# TODO: How to account for Chinese translations in the output? (Maybe retranslate in these cases? Work on the prompt?)

import chunking
from tqdm import tqdm

import time
import subprocess, os

# import anthropic
from translationmodels.openai import OpenAITranslator
from translationmodels.anthropic import AnthropicTranslator
from translationmodels.llama import LlamaTranslator
from translationmodels.deepseek import DeepSeekTranslator


# Configuration class to hold API clients
class Config:
    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.llama_client = None
        self.deepseek_client = None
        self.gemini_client = None

config = Config()

# takes a parameter string and uses the OpenAI API to translate it to English (later added more api options)
# from Classical Chinese (if the USE_AI constant is set to True)
# TODO: Update this to work more consistently with multiple AI models, and better with olllama models
# TODO: Support HuggingFace models as well?
def translate(text, aimodel):
    if "gpt" in aimodel.lower() and "gpt-oss" not in aimodel.lower(): # Make an OPENAI api call
        if config.openai_client is None:
            print("Error: OpenAI client not initialized. Provide a valid API key.")
            return None
        return config.openai_client.translate(text, aimodel)
    elif "claude" in aimodel.lower():
        if config.anthropic_client is None:
            print("Error: Anthropic client not initialized. Provide a valid API key.")
            return None
        return config.anthropic_client.translate(text, aimodel)
    elif "gemini" in aimodel.lower():
        if config.gemini_client is None:
            print("Error: Gemini client not initialized. Provide a valid API key.")
            return None
        return config.gemini_client.translate(text, aimodel)
    elif "llama" in aimodel.lower():
        if config.llama_client is None:
            print("Error: Llama client not initialized.")
            return None
        return config.llama_client.translate(text, aimodel)
    elif "deepseek" in aimodel.lower():
        if config.deepseek_client is None:
            print("Error: Deepseek client not initialized")
            return None
        return config.deepseek_client.translate(text, aimodel)
    else:
        if config.llama_client is None:
            print("Error: ollama client not initialized.")
            return None
        return config.llama_client.translate(text, aimodel)
        # print("Error: Unrecognized model selection.")
        # return None
    
# this will iterate through the chunks and translate them one by one, returning two lists: untranslated and translated
def translate_chunks(untranslated_chunks, aimodel):
    translated_chunks = []
    if not untranslated_chunks:  # empty deque or list
        print("You gave an empty document!")
    else:
        with tqdm(total=len(untranslated_chunks)) as pbar:
            for chunk in untranslated_chunks:
                translated_text = translate(chunk, aimodel)
                translated_chunks.append(translated_text)
                pbar.update(1)

    return untranslated_chunks, translated_chunks

import os
import time

# This function generates and saves the translated txt file
# TODO: Edit the first line to have more metadata (must integrate into the web UI later)
def generate_txt(chinese_untranslated, english_translated, directory_path, aimodel, output_filepath_name):
    english_length = 0
    chinese_length = 0

    write_path = os.path.join(directory_path, f"{output_filepath_name}.txt")
    if chinese_untranslated and english_translated:
        with open(write_path, "w", encoding="utf-8") as file:

            file.write(f"Translation created with model: {aimodel} \n\n")

            # english section
            node_counter = 1
            for eng_text in english_translated:
                file.write(eng_text + '[' + str(node_counter) + "p]" + '\n')
                english_length += len(eng_text)
                node_counter += 1

            # intermediate section
            file.write("\n\nBelow is the original Chinese:\n\n\n")

            # chinese section
            node_counter = 1
            for zh_text in chinese_untranslated:
                file.write(zh_text + '[' + str(node_counter) + "p]" + '\n')
                chinese_length += len(zh_text)
                node_counter += 1
        file.write("\n\n\n\nSummary Statistics\n")
        file.write("\tTotal English characters: " + str(english_length))
        file.write("\tTotal Chinese characters: " + str(chinese_length))
        file.write("\tAverage English chunk length: " + str(round(sum(len(c) for c in english_translated) / len(english_translated), 2)) if english_translated else "0")
        file.write("\tAverage Chinese chunk length: " + str(round(sum(len(c) for c in chinese_untranslated) / len(chinese_untranslated), 2)) if chinese_untranslated else "0")
        file.write("\tTotal: " + str(chinese_length + english_length))
        file.write(f"File saved to: {write_path}")
    else:
        print("Your file is probably empty or something! Figure this out")

# Initializes appropriate API clients based on the selected model
# TODO: Streamline this function / combine with translate function somehow?
def initialize_clients(aimodel, api_key=None):

    if ("gpt" in aimodel.lower() or aimodel.startswith("o")) and "gpt-oss" not in aimodel.lower():
        # OpenAI
        if not api_key or api_key == "Paste OpenAI API key here":
            print("Paste your OpenAI API key in the designated area")
        else:
            if config.openai_client is None:
                config.openai_client = OpenAITranslator(api_key=api_key)

    elif "claude" in aimodel.lower():
        # Anthropic
        if not api_key or api_key == "Paste Anthropic API key here":
            print("Paste your Anthropic API key in the designated area")
        else:
            if config.anthropic_client is None:
                config.anthropic_client = AnthropicTranslator(api_key=api_key)

    elif "gemini" in aimodel.lower():
        # Gemini
        if not api_key or api_key == "Paste Gemini API key here":
            print("Paste your Gemini API key in the designated area")
        else:
            if config.gemini_client is None:
                from translationmodels.gemini import GeminiTranslator
                config.gemini_client = GeminiTranslator(api_key=api_key)

    elif "llama" in aimodel.lower():
        # Llama (local or API-based)
        if config.llama_client is None:
            config.llama_client = LlamaTranslator(model=aimodel)

    elif "deepseek" in aimodel.lower():
        # DeepSeek
        if config.deepseek_client is None:
            config.deepseek_client = DeepSeekTranslator(model=aimodel)

    else:
        # Default to Ollama local Llama
        if config.llama_client is None:
            config.llama_client = LlamaTranslator(model=aimodel)

def translate_file(filepath, output_directory, aimodel, api_key, output_filepath_name="DEFAULT"):
    base_name = os.path.splitext(os.path.basename(filepath))[0]

    if output_filepath_name == "DEFAULT":
        output_filepath_name = f"{base_name}_translated"

    initialize_clients(aimodel, api_key)

    # 1. Chunking- This is conducted in chunking.py, and will result in translatable chunks.
    chunks = chunking.chunk_file(filepath)
    print(len(chunks))
    # 2. Translation- This will result in translated chunks.
    untranslated_chunks, translated_chunks = translate_chunks(chunks, aimodel)
    # 3. TXT Generation- This will result in a saved txt file with the translated and untranslated chunks.
    generate_txt(untranslated_chunks, translated_chunks, output_directory, aimodel, output_filepath_name)

# if __name__ == "__main__": # Example implementation
#     FILEPATH = '古今图书集成博物汇编艺术典医部全录/中恶门.txt'
#     DIRECTORY_PATH = 'translations_output'
#     AI_MODEL = 'gpt-4o-mini-2024-07-18'
#     API_KEY = 'api key here'
#     translate_file(FILEPATH, DIRECTORY_PATH, AI_MODEL, API_KEY)
