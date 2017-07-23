import requests


DOG_API = 'https://dog.ceo/api'


class Doggo:
    def __init__(self, url=DOG_API):
        self.url = url

    def list(self):
        r = requests.get("%s/breeds/list" % self.url)
        res = r.json()
        return '\n'.join(res['message'])

    def random(self, breed=None):
        if breed == None:
            r = requests.get("%s/breeds/image/random" % self.url)
        else:
            r = requests.get("%s/breed/%s/images/random" % (self.url, breed))

        res = r.json()
        if res['code'] == "404":
            return None
        else:
            return res['message']
