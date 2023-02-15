import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import sqlite3
import os


def get_soup(url):
    r = requests.get(url)
    if r.status_code == 200:
        return bs(r.content, 'html.parser')
    else:
        raise Exception("Error: could not connect to website")


def get_teams_dict(soup):
    teams = soup.find_all('li', {'class': 'alt'})
    teams_dict = {}
    for team in teams:
        link = 'https://www.soccerbase.com' + team.find('a')['href']
        name = team.text
        teams_dict[name] = link
    return teams_dict


def get_team_data(soup, name, link):
    headers = ['Team', 'Competition', 'Home Team', 'Home Score', 'Away Team', 'Away Score', 'Date Keep']
    h_scores = [int(i.text) for i in soup.select('.score a em:first-child')]
    a_scores = [int(i.text) for i in soup.select('.score a em + em')]
    limit = len(a_scores)
    team = [name for i in soup.select('.tournament', limit=limit)]
    comps = [i.text for i in soup.select('.tournament a', limit=limit)]
    dates = [i.text for i in soup.select('.dateTime .hide', limit=limit)]
    h_teams = [i.text for i in soup.select('.homeTeam a', limit=limit)]
    a_teams = [i.text for i in soup.select('.awayTeam a', limit=limit)]
    df = pd.DataFrame(list(zip(team, comps, h_teams, h_scores, a_teams, a_scores, dates)), columns=headers)
    return df


def save_data_to_db(data, db_path):
    con = sqlite3.connect(db_path)
    for df in data:
        df.to_sql("datos", con, if_exists="append")
    con.commit()
    con.close()


if __name__ == '__main__':
    url = 'https://www.soccerbase.com/teams/home.sd'
    try:
        soup = get_soup(url)
    except Exception as e:
        print(str(e))
        exit()

    teams_dict = get_teams_dict(soup)
    data = []
    for name, link in teams_dict.items():
        if 'javascript: void(0);' in link or '/tournaments/tournament.sd' in link:
            continue
        try:
            soup = get_soup('%s&teamTabs=results' % link)
            df = get_team_data(soup, name, link)
            data.append(df)
            print(df)
            os.system('clear')
        except Exception as e:
            print(str(e))

    db_path = "datos.db"
    save_data_to_db(data, db_path)
    print("Data saved to file")
