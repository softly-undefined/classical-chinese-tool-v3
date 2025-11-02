import google.generativeai as genai
import os

class GeminiTranslator:
    def __init__(self, api_key=None, aimodel='gemini-2.5-flash-lite'):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is missing. Set it as an environment variable or pass it as an argument.")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(aimodel)

    def translate(self, text, max_tokens=1000, temperature=0):
        try:
            prompt_parts = [
                "Translate the following Classical Chinese text to English with a focus on accuracy. Only output the translation:",
                f"\n\nClassical Chinese Text:\n{text}",
                "\n\nEnglish Translation:"
            ]
            
            response = self.model.generate_content(
                prompt_parts,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature
                )
            )
            return response.text
        except Exception as e:
            print(f"Error during translation: {e}")
            return None