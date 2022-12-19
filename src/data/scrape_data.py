# Scrapes the data from plusLiga's website
import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np


def get_match_urls(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text)
    match_table = soup.find(id='table-small')
    table_links = match_table.find_all('a')
    links = [link.get('href') for link in table_links]
    links = [link for link in links if '/games/' in link]
    match_urls = [f'https://www.plusliga.pl{link}' for link in links]

    return match_urls


def get_game_data(game_url):
    r = requests.get(game_url)
    soup = BeautifulSoup(r.text)

    teams = soup.find_all('h3')
    teams = teams[-3:-1]
    team1 = teams[0].get_text()
    team2 = teams[1].get_text()

    table1, table2 = soup.find_all('table')[:2]

    last_row = [row.get_text() for row in table1.find_all('tr')[-1]]
    last_row_cleaned = [e for e in last_row if e not in ['\n', 'Łącznie', '\xa0']]
    last_row2 = [row.get_text() for row in table2.find_all('tr')[-1]]
    last_row_cleaned2 = [e for e in last_row2 if e not in ['\n', 'Łącznie', '\xa0']]

    game_result = soup.find_all('div',{'class':'gameresult'})[-1].get_text().split()
    team1_score = game_result[0]
    team2_score = game_result[-1]

    game_date = soup.find_all('div', {'class': 'khanded'})[-1].get_text().strip()
    full_row_data = [game_date, team1, team2, team1_score, team2_score] + last_row_cleaned + last_row_cleaned2

    return full_row_data


seasons_urls = ['https://www.plusliga.pl/games/tour/2022.html?memo=%7B%22games%22%3A%7B%7D%7D',
                'https://www.plusliga.pl/games/tour/2021.html',
                'https://www.plusliga.pl/games/tour/2020.html'
                'https://www.plusliga.pl/games/tour/2019.html',
                'https://www.plusliga.pl/games/tour/2018.html',
                'https://www.plusliga.pl/games/tour/2017.html',
                'https://www.plusliga.pl/games/tour/2016.html',
                'https://www.plusliga.pl/games/tour/2015.html',
                'https://www.plusliga.pl/games/tour/2014.html',
                'https://www.plusliga.pl/games/tour/2013.html',
                'https://www.plusliga.pl/games/tour/2012.html',
                'https://www.plusliga.pl/games/tour/2011.html',
                'https://www.plusliga.pl/games/tour/2010.html',
                'https://www.plusliga.pl/games/tour/2008.html',
                'https://www.plusliga.pl/games/tour/2009.html']


all_match_urls = [get_match_urls(url) for url in seasons_urls]
all_match_urls_clean = [item for sublist in all_match_urls for item in sublist]

column_names = ['Date', 'Team_1', 'Team_2', 'T1_Score', 'T2_Score', 'T1_Sum', 'T1_BP', 'T1_Ratio', 'T1_Srv_Sum',
                'T1_Srv_Err', 'T1_Srv_Ace', 'T1_Srv_Eff', 'T1_Rec_Sum', 'T1_Rec_Err', 'T1_Rec_Pos', 'T1_Rec_Perf',
                'T1_Att_Sum', 'T1_Att_Err', 'T1_Att_Blk', 'T1_Att_Kill', 'T1_Att_Kill_Perc', 'T1_Att_Eff', 'T1_Blk_Sum',
                'T1_Blk_As', 'T2_Sum', 'T2_BP', 'T2_Ratio', 'T2_Srv_Sum', 'T2_Srv_Err', 'T2_Srv_Ace', 'T2_Srv_Eff',
                'T2_Rec_Sum', 'T2_Rec_Err', 'T2_Rec_Pos', 'T2_Rec_Perf', 'T2_Att_Sum', 'T2_Att_Err', 'T2_Att_Blk',
                'T2_Att_Kill', 'T2_Att_Kill_Perc', 'T2_Att_Eff', 'T2_Blk_Sum', 'T2_Blk_As']

all_match_data = np.array(column_names)
counter = 0
for match_url in all_match_urls_clean:
    game_data = get_game_data(match_url)

    # Filters out matches that haven't benn played yet
    if len(game_data) == len(column_names):
        counter += 1
        all_match_data = np.vstack((all_match_data, game_data))
        print(f'Scraped {counter}/{len(all_match_urls_clean)}')


df = pd.DataFrame(all_match_data[1:], columns=all_match_data[0]).set_index('Date')
df.to_csv('data.csv')



