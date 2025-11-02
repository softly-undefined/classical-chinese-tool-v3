from langchain_ollama import ChatOllama
import os
import re

class DeepSeekTranslator:
    def __init__(self, model="deepseek-r1:7b", temperature=0, max_tokens=1200):
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

        # enforce hard cap with model_kwargs
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

            # strip DeepSeek R1's <think> reasoning blocks
            final_answer = re.sub(
                r"<think>.*?</think>\s*",
                "",
                response.content,
                flags=re.DOTALL
            ).strip()

            return final_answer
        except Exception as e:
            print(f"Error during translation with DeepSeek: {e}")
            return None
