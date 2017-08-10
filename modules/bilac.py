import requests


BILAC = 'https://bilac.theanht1.me/api/v2'


def member_info(mem):
    return "%s: %s" % (mem['username'], mem['elo'])

def team_name(team):
    return "%s + %s" % (team['Member1']['username'], team['Member2']['username'])

def find(teams, id):
    for team in teams:
        if team['ID'] == id:
            return team

class Bilac:
    def __init__(self, url=BILAC):
        self.url = url

    def elo(self):
        r = requests.get("%s/members?sort=-elo" % self.url)
        res = r.json()
        return map(member_info, res)

    def next_match(self):
        r = requests.get("%s/tournaments" % self.url)
        tour_id = r.json()[0]['ID']

        r = requests.get("%s/tournaments/%d" % (self.url, tour_id))
        res = r.json()

        matches = res['Matches']
        teams = res['Teams']

        for match in matches:
            if match['Team1Score'] == -1 or match['Team2Score'] == -1:
                team1 = find(teams, match['Team1ID'])
                team2 = find(teams, match['Team2ID'])
                return "%s VS %s" % (team_name(team1), team_name(team2))

        return "All matches done"
