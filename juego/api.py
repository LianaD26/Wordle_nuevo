import requests
class WordFetcher:
    def get_random_word(self, length):
        random_word_api_url = "https://random-word-api.herokuapp.com/word"
        random_word_api_response = requests.get(random_word_api_url, params={"length": length, "lang": "en"})
        random_word = random_word_api_response.json()[0]
        return random_word

    def get_word_definition(self, word):
        url = "https://api.dictionaryapi.dev/api/v2/entries/en/{}"
        response = requests.get(url.format(word))
        return response

    def get_random_word_with_meaning(self, length):
        status_code = 404

        while status_code != 200:
            word = self.get_random_word(length)
            meaning_response = self.get_word_definition(word)
            status_code = meaning_response.status_code

        definition = meaning_response.json()[0]["meanings"][0]["definitions"][0]["definition"]

        random_word = {
            'word': word,
            'definition': definition
        }

        return random_word
