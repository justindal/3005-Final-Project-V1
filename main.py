import json
import psycopg


# Competition and seasons stored in competitions.json
# Matches for each competition and season, stored in matches. Each folder within is named for a competition ID,
# each file is named for a season ID within that competition.
# Events and lineups for each match, stored in events and lineups respectively. Each file is named for a match ID.
def get_relevant_data() -> []:
    competition_ids = []
    season_ids = []

    with open('open-data/data/competitions.json') as f:
        data = json.load(f)
        for competition in data:
            c1 = competition['competition_name'] == 'La Liga' and competition['season_name'] in ['2020/2021',
                                                                                                 '2019/2020',
                                                                                                 '2018/2019']
            c2 = competition['competition_name'] == 'Premier League' and competition['season_name'] == '2003/2004'
            if c1 or c2:
                for item in competition:
                    # print(item + ':', competition[item])
                    if item == 'competition_id':
                        competition_ids.append(competition[item])
                    if item == 'season_id':
                        season_ids.append(competition[item])
                # print('---')

    if len(competition_ids) == 0 or len(season_ids) == 0:
        raise ValueError('No competition or season IDs found')

    # matches for each competition and season

    match_file_paths = []
    match_ids = []

    for i in range(len(competition_ids)):
        match_file_paths.append(
            'open-data/data/matches/' + str(competition_ids[i]) + '/' + str(season_ids[i]) + '.json')

    for file_path in match_file_paths:
        with open(file_path) as f:
            data = json.load(f)
            for match in data:
                for item in match:
                    # print(item + ':', match[item])
                    if item == 'match_id':
                        match_ids.append(match[item])

    # events and lineups for each match
    event_file_paths = []
    lineup_file_paths = []

    for match_id in match_ids:
        event_file_paths.append('open-data/data/events/' + str(match_id) + '.json')
        lineup_file_paths.append('open-data/data/lineups/' + str(match_id) + '.json')

    return [competition_ids, season_ids, match_ids, match_file_paths, event_file_paths, lineup_file_paths]


# data from competitions.json
def populate_from_competitions(cursor: psycopg.cursor):
    with open('open-data/data/competitions.json') as f:
        data = json.load(f)
        for competition in data:
            c1 = competition['competition_name'] == 'La Liga' and competition['season_name'] in ['2020/2021',
                                                                                                 '2019/2020',
                                                                                                 '2018/2019']
            c2 = competition['competition_name'] == 'Premier League' and competition['season_name'] == '2003/2004'
            if c1 or c2:
                # seasons
                cursor.execute(
                    'INSERT INTO season (competition_id, season_id, season_name) VALUES (%s, %s, %s)',
                    (competition['competition_id'], competition['season_id'], competition['season_name'])
                )

                # competitions
                cursor.execute(
                    'INSERT INTO competition (competition_id, competition_name, competition_gender, '
                    'competition_youth, competition_international, season_id, country_name)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                    (
                        competition['competition_id'], competition['competition_name'],
                        competition['competition_gender'],
                        competition['competition_youth'], competition['competition_international'],
                        competition['season_id'], competition['country_name'])
                )


# data from matches folder TODO not finished
def populate_from_matches(cursor: psycopg.cursor, match_file_paths: []):
    for file in match_file_paths:
        with open(file) as f:
            data = json.load(f)
            for match in data:
                # add teams to database
                cursor.execute(
                    'INSERT INTO team (team_id, team_name, team_gender, team_group, country_id) '
                    'VALUES (%s, %s, %s, %s, %s)',
                    (
                        match['home_team']['home_team_id'], match['home_team']['home_team_name'],
                        match['home_team']['home_team_gender'], match['home_team']['home_team_group'],
                        match['home_team']['country']['id'])
                )

                # add match to database
                referee_id = match['referee']['id'] if 'referee' in match else None
                cursor.execute(
                    'INSERT INTO match (match_id, match_date, kick_off, home_score, away_score, match_week, '
                    'competition_id, home_team_id, away_team_id, competition_stage_id, stadium_id, referee_id, '
                    'home_manager_id, away_manager_id, season_id)'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (
                        match['match_id'],
                        match['match_date'],
                        match['kick_off'],
                        match['home_score'],
                        match['away_score'],
                        match['match_week'],
                        match['competition']['competition_id'],
                        match['home_team']['home_team_id'],
                        match['away_team']['away_team_id'],
                        match['competition_stage']['id'],
                        match['stadium']['id'],
                        referee_id,
                        match['home_team']['managers'][0]['id'],
                        match['away_team']['managers'][0]['id'],
                        match['season']['season_id']
                    )
                )


def create_tables(cursor: psycopg.cursor):
    # get file named createTables.sql
    with open('createTables.sql', 'r') as file:
        sql = file.read()
        cursor.execute(sql)


def main():
    connection = psycopg.connect(
        host='localhost',
        dbname='PROJECT'
    )
    cursor = connection.cursor()

    data = get_relevant_data()
    # createTables(cursor)
    # populate_from_competitions(cursor)
    populate_from_matches(cursor, data[3])
    # print(data[3][0])

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
