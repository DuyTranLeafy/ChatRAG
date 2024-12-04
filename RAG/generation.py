import openai


class LanguageModel:
    def __init__(self, api_key, model_name='gpt-3.5-turbo'):
        self.api_key = api_key
        self.model_name = model_name

    def get_response(self, prompt):
        openai.api_key = self.api_key
        openai.base_url = "http://localhost:3040/v1/"
        response = openai.ChatCompletion.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message['content']
