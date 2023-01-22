import openai
import json

with open('./secrets.json') as file:
    secrets = json.loads(file.read())

openai.api_key = secrets["apiKey"]

class OpenAIModel():
    def __init__(self):
        self.history = ["Clippy is an AI assistant"]
        self.tipModifier = ''

        # Define AI Options
        self.defaultConfig = {
            "engine": "text-davinci-003",
            "temperature": 0.5,
            "max_tokens": 512,
            "top_p": 1,
            "frequency_penalty": 0,
            "presence_penalty": 0,
            "useMemory": True
        }
        self.config = self.defaultConfig

    def reset(self):
        self.history = self.history[:1]

    def generateTip(self, prompt):
        try:
            completion = openai.Completion.create(engine=self.model, prompt='\n'.join(self.history))
            response = completion.choices[0].text
            response = response.strip()
        except openai.error.RateLimitError as e:
            response = "[RATELIMITED]\nOur server are overloaded!"

    def prompt(self, prompt):
        prompt = prompt.strip()
        self.history.append("User: " + prompt)
        self.history.append("Response: ")

        while True:
            try:
                completion = openai.Completion.create(
                    engine=self.config["engine"],
                    prompt='\n'.join(self.history), #prompt
                    temperature=self.config["temperature"],
                    max_tokens=self.config["max_tokens"],
                    top_p=self.config["top_p"],
                    frequency_penalty=self.config["frequency_penalty"],
                    presence_penalty=self.config["presence_penalty"],
                )
                #completion = openai.Completion.create(engine=self.model, prompt='\n'.join(self.history))
                response = completion.choices[0].text
                response = response.strip()

                self.history[-1] = "Response: " + response
                break
            except openai.error.RateLimitError as e:
                response = "[RATELIMITED]\nOur server are overloaded! Please wait a bit."
                break
            except openai.error.InvalidRequestError as e:
                self.history = self.history[3:-3]

        return response