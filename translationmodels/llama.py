from langchain_ollama import ChatOllama
import os

class LlamaTranslator:
    def __init__(self, model="llama3.1", temperature=0, max_tokens=1200):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # num_predict is the Ollama equivalent of max_tokens
        self.client = ChatOllama(
            model=self.model,
            temperature=self.temperature,
            model_kwargs={"num_predict": self.max_tokens}
        )

    def translate(self, text, aimodel=None):
        try:
            response = self.client.invoke(
                f"Translate the following Classical Chinese text to English with a focus on accuracy, and no notes other than the translated text: {text}"
            )
            return response.content  # Extracts text from the response
        except Exception as e:
            print(f"Error during translation with Llama: {e}")
            return None
