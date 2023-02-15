import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import sqlite3

url = 'https://www.soccerbase.com/teams/home.sd'
r = requests.get(url)
if r.status_code == 200:
    soup = bs(r.content, 'html.parser')
else:
    print("Error: could not connect to website")
    exit()

teams = soup.find_all('li', {'class': 'alt'})
teams_dict = {}
for team in teams:
    link = 'https://www.soccerbase.com' + team.find('a')['href']
    team = team.text
    teams_dict[team] = link

consolidated = []
for k, v in teams_dict.items():
    if 'javascript: void(0);' in v:
        continue
    if '/tournaments/tournament.sd' in v:
        continue
    headers = ['Team', 'Competition', 'Home Team', 'Home Score', 'Away Team', 'Away Score', 'Date Keep']
    r = requests.get('%s&teamTabs=results' % v)
    soup = bs(r.content, 'html.parser')
    h_scores = [int(i.text) for i in soup.select('.score a em:first-child')]
    a_scores = [int(i.text) for i in soup.select('.score a em + em')]
    limit = len(a_scores)
    team = [k for i in soup.select('.tournament', limit=limit)]
    comps = [i.text for i in soup.select('.tournament a', limit=limit)]
    dates = [i.text for i in soup.select('.dateTime .hide', limit=limit)]
    h_teams = [i.text for i in soup.select('.homeTeam a', limit=limit)]
    a_teams = [i.text for i in soup.select('.awayTeam a', limit=limit)]
    df = pd.DataFrame(list(zip(team, comps, h_teams, h_scores, a_teams, a_scores, dates)),columns=headers)
    consolidated.append(df)
    print(df)
con = sqlite3.connect("datos.db")
cursor = con.cursor()
for df in consolidated:
    df.to_sql("datos", con, if_exists="append")
con.commit()
con.close()


print("Data saved to file")
