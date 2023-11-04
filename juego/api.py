import requests, json
class WordFetcher:
    def __init__(self):
        self.api_url = "https://random-word-api.herokuapp.com/word"

    def get_random_word(self):
        response = requests.get(self.api_url, params={"length": 5, "lang": "en"})# solicitud a la API

        random_word = response.json()[0]
        return random_word

    def get_word_definition(self, word):
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
        response = requests.get(url.format(word))
        return response

    def get_random_word_with_meaning(self):
        status_code = 404

        while status_code != 200:
            word = self.get_random_word()
            meaning_response = self.get_word_definition(word)
            status_code = meaning_response.status_code

        definition = meaning_response.json()[0]["meanings"][0]["definitions"][0]["definition"]

        random_word = {
            'word': word,
            'definition': definition
        }

        return random_word
