import requests

class WordFetcher:
    def __init__(self):
        self.api_url = "https://random-word-api.herokuapp.com/word"

    def get_random_word(self):
        random_word_api_url = "https://random-word-api.herokuapp.com/word"

        try:
            random_word_api_response = requests.get(
                random_word_api_url, params={"length": 5, "lang": "en"})
            random_word_api_response.raise_for_status()  #errores HTTP
            random_word = random_word_api_response.json()[0]
            return random_word
        except requests.exceptions.RequestException as e:
            print("Error al hacer la solicitud HTTP:", e)
            return None

    def get_word_definition(self, word):
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
        try:
            response = requests.get(url.format(word))
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print("Error al hacer la solicitud HTTP:", e)
            return None

    def get_random_word_with_meaning(self):
        status_code = 404

        while status_code != 200:
            word = self.get_random_word()
            meaning_response = self.get_word_definition(word)
            status_code = meaning_response.status_code

        definition = meaning_response.json()[0]["meanings"][0]["definitions"][0]["definition"]

        return definition
