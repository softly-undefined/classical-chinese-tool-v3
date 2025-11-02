from openai import OpenAI
import os

class OpenAITranslator:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key is missing. Set it as an environment variable or pass it as an argument.")
        self.client = OpenAI(api_key=self.api_key)

    def translate(self, text, model, max_completion_tokens=1000, temperature=0):
        try:
            response = self.client.responses.create(
                model=model,
                input=[
                    {"role": "system", "content": "Translate the following Classical Chinese text to English with a focus on accuracy:"},
                    {"role": "user", "content": text}
                ],
                max_output_tokens=max_completion_tokens,
            )
            return response.output_text
        except Exception as e:
            print(f"Error during translation: {e}")
            return None
