import requests


DOG_API = 'https://dog.ceo/api'


class Doggo:
    def __init__(self, url=DOG_API):
        self.url = url

    def random(self):
        r = requests.get("%s/breeds/image/random" % self.url)
        res = r.json()
        return res['message']
