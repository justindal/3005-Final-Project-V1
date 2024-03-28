import json
import psycopg
import datetime as dt

competition_ids = []
season_ids = []

# Competition and seasons stored in competitions.json
# Matches for each competition and season, stored in matches. Each folder within is named for a competition ID, each file is named for a season ID within that competition.
# Events and lineups for each match, stored in events and lineups respectively. Each file is named for a match ID.


with open ('open-data/data/competitions.json') as f:
    data = json.load(f)
    for competition in data:
        c1 = competition['competition_name'] == 'La Liga' and competition['season_name'] in ['2020/2021', '2019/2020', '2018/2019']
        c2 = competition['competition_name'] == 'Premier League' and competition['season_name'] == '2003/2004'
        if c1 or c2:
            for item in competition:
                print(item + ':', competition[item])
                if item == 'competition_id':
                    competition_ids.append(competition[item])
                if item == 'season_id':
                    season_ids.append(competition[item])
            print('---')


if len(competition_ids) == 0 or len(season_ids) == 0:
    raise ValueError('No competition or season IDs found')


for competition_id in competition_ids:
    for season_id in season_ids:
        with open(f'open-data/data/matches/{competition_id}/{season_id}.json') as f:
            data = json.load(f)
            for match in data:
                for item in match:
                    print(item + ':', match[item])
                print('---')
        break
    break
    
    
                    


                

print(competition_ids)
print(season_ids)

def main():
    connection = psycopg.connect(
        host='localhost',
        database='PROJECT'
    )
    cursor = connection.cursor()

    # createTables(cursor)

    connection.commit()
    cursor.close()
    connection.close()

def createTables(cursor: psycopg.cursor):
    # get file named createTables.sql
    # with open('createTables.sql', 'r') as f:
    #     sql = f.read()
    #     cursor.execute(sql)
    pass




