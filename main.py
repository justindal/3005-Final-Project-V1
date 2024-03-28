import json
import psycopg
import datetime as dt


# Competition and seasons stored in competitions.json
# Matches for each competition and season, stored in matches. Each folder within is named for a competition ID, each file is named for a season ID within that competition.
# Events and lineups for each match, stored in events and lineups respectively. Each file is named for a match ID.

competition_ids = []
season_ids = []

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

# matches for each competition and season

match_file_paths = []
match_ids = []

for i in range(len(competition_ids)):
    match_file_paths.append('open-data/data/matches/' + str(competition_ids[i]) + '/' + str(season_ids[i]) + '.json')
        
for file_path in match_file_paths:
    with open(file_path) as f:
        data = json.load(f)
        for match in data:
            for item in match:
                print(item + ':', match[item])
                if item == 'match_id':
                    match_ids.append(match[item])
            print('---')

    
# events and lineups for each match
event_file_paths = []
lineup_file_paths = []

for match_id in match_ids:
    event_file_paths.append('open-data/data/events/' + str(match_id) + '.json')
    lineup_file_paths.append('open-data/data/lineups/' + str(match_id) + '.json')   

print(f'Competition IDs: {competition_ids}')
print(f'Season IDs: {season_ids}')
print(f'Match IDs: {match_ids}')
# print(f'Match file paths: {match_file_paths}')
# print(f'Event file paths: {event_file_paths}')
# print(f'Lineup file paths: {lineup_file_paths}')


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
    with open('createTables.sql', 'r') as f:
        sql = f.read()
        cursor.execute(sql)




