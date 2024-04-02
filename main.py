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
def populate_from_competitions(cursor: psycopg.cursor) -> None:
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


# data from matches folder
def populate_from_matches(cursor: psycopg.cursor, match_file_paths: []):
    for file in match_file_paths:
        with open(file) as f:
            data = json.load(f)
            for match in data:
                print(f'match: {match["match_id"]} and file: {file}')
                # Check if 'referee' key exists in match
                if 'referee' in match:
                    # check if referee exists
                    cursor.execute('SELECT referee_id FROM referee WHERE referee_id = %s',
                                   (match['referee']['id'],))
                    referee = cursor.fetchone()
                    if referee is None:
                        cursor.execute(
                            'INSERT INTO referee (referee_id, referee_name) VALUES (%s, %s)',
                            (match['referee']['id'], match['referee']['name'])
                        )

                # Check if 'managers' key exists in home team and it's not empty
                if 'managers' in match['home_team'] and len(match['home_team']['managers']) > 0:
                    for manager in match['home_team']['managers']:
                        # Check if manager's country exists
                        cursor.execute('SELECT country_id FROM countries WHERE country_id = %s',
                                       (manager['country']['id'],))
                        country = cursor.fetchone()
                        if country is None:
                            # add country to database
                            cursor.execute(
                                'INSERT INTO countries (country_id, country_name) '
                                'VALUES (%s, %s)',
                                (
                                    manager['country']['id'],
                                    manager['country']['name']
                                )
                            )
                        # check if home manager exists
                        cursor.execute('SELECT manager_id FROM manager WHERE manager_id = %s',
                                       (manager['id'],))
                        manager_in_db = cursor.fetchone()
                        if manager_in_db is None:
                            cursor.execute(
                                'INSERT INTO manager (manager_id, manager_name, country_id) VALUES (%s, %s, %s)',
                                (manager['id'], manager['name'], manager['country']['id'])
                            )

                # Check if 'managers' key exists in away team and it's not empty
                if 'managers' in match['away_team'] and len(match['away_team']['managers']) > 0:
                    for manager in match['away_team']['managers']:
                        # Check if manager's country exists
                        cursor.execute('SELECT country_id FROM countries WHERE country_id = %s',
                                       (manager['country']['id'],))
                        country = cursor.fetchone()
                        if country is None:
                            # add country to database
                            cursor.execute(
                                'INSERT INTO countries (country_id, country_name) '
                                'VALUES (%s, %s)',
                                (
                                    manager['country']['id'],
                                    manager['country']['name']
                                )
                            )
                        # check if away manager exists
                        cursor.execute('SELECT manager_id FROM manager WHERE manager_id = %s',
                                       (manager['id'],))
                        manager_in_db = cursor.fetchone()
                        if manager_in_db is None:
                            cursor.execute(
                                'INSERT INTO manager (manager_id, manager_name, country_id) VALUES (%s, %s, %s)',
                                (manager['id'], manager['name'], manager['country']['id'])
                            )

                # check if stadium in match
                if 'stadium' in match:
                    # check if stadium country exists
                    cursor.execute('SELECT country_id FROM countries WHERE country_id = %s',
                                   (match['stadium']['country']['id'],))
                    country = cursor.fetchone()
                    if country is None:
                        # add country to database
                        cursor.execute(
                            'INSERT INTO countries (country_id, country_name) '
                            'VALUES (%s, %s)',
                            (
                                match['stadium']['country']['id'],
                                match['stadium']['country']['name']
                            )
                        )

                    # check if stadium exists
                    cursor.execute('SELECT stadium_id FROM stadium WHERE stadium_id = %s',
                                   (match['stadium']['id'],))
                    stadium = cursor.fetchone()
                    if stadium is None:
                        # add stadium to database
                        cursor.execute(
                            'INSERT INTO stadium (stadium_id, stadium_name, country_id) '
                            'VALUES (%s, %s, %s)',
                            (
                                match['stadium']['id'],
                                match['stadium']['name'],
                                match['stadium']['country']['id']
                            )
                        )

                # check if competition stage exists
                cursor.execute('SELECT competition_stage_id FROM competition_stage WHERE competition_stage_id = %s',
                               (match['competition_stage']['id'],))
                competition_stage = cursor.fetchone()
                if competition_stage is None:
                    # add competition stage to database
                    cursor.execute(
                        'INSERT INTO competition_stage (competition_stage_id, competition_stage_name) VALUES (%s, %s)',
                        (match['competition_stage']['id'], match['competition_stage']['name'])
                    )

                # Check if home team's country exists
                cursor.execute('SELECT country_id FROM countries WHERE country_id = %s',
                               (match['home_team']['country']['id'],))
                country = cursor.fetchone()
                if country is None:
                    # add country to database
                    cursor.execute(
                        'INSERT INTO countries (country_id, country_name) '
                        'VALUES (%s, %s)',
                        (
                            match['home_team']['country']['id'],
                            match['home_team']['country']['name']
                        )
                    )

                # Check if away team's country exists
                cursor.execute('SELECT country_id FROM countries WHERE country_id = %s',
                               (match['away_team']['country']['id'],))
                country = cursor.fetchone()
                if country is None:
                    # add country to database
                    cursor.execute(
                        'INSERT INTO countries (country_id, country_name) '
                        'VALUES (%s, %s)',
                        (
                            match['away_team']['country']['id'],
                            match['away_team']['country']['name']
                        )
                    )

                # Check if home team exists
                cursor.execute('SELECT team_id FROM team WHERE team_id = %s', (match['home_team']['home_team_id'],))
                home_team = cursor.fetchone()
                if home_team is None:
                    # add team to database
                    cursor.execute(
                        'INSERT INTO team (team_id, team_name, team_gender, team_group, country_id) '
                        'VALUES (%s, %s, %s, %s, %s)',
                        (
                            match['home_team']['home_team_id'],
                            match['home_team']['home_team_name'],
                            match['home_team']['home_team_gender'],
                            match['home_team']['home_team_group'],
                            match['home_team']['country']['id']
                        )
                    )

                # Check if away team exists
                cursor.execute('SELECT team_id FROM team WHERE team_id = %s', (match['away_team']['away_team_id'],))
                away_team = cursor.fetchone()
                if away_team is None:
                    # add team to database
                    cursor.execute(
                        'INSERT INTO team (team_id, team_name, team_gender, team_group, country_id) '
                        'VALUES (%s, %s, %s, %s, %s)',
                        (
                            match['away_team']['away_team_id'],
                            match['away_team']['away_team_name'],
                            match['away_team']['away_team_gender'],
                            match['away_team']['away_team_group'],
                            match['away_team']['country']['id']
                        )
                    )

                # add match to database
                referee_id = match['referee']['id'] if 'referee' in match else None
                stadium_id = match['stadium']['id'] if 'stadium' in match else None

                # Check if 'managers' key exists in home team and it's not empty
                if 'managers' in match['home_team'] and len(match['home_team']['managers']) > 0:
                    home_manager_id = match['home_team']['managers'][0]['id']
                else:
                    home_manager_id = None

                # Check if 'managers' key exists in away team and it's not empty
                if 'managers' in match['away_team'] and len(match['away_team']['managers']) > 0:
                    away_manager_id = match['away_team']['managers'][0]['id']
                else:
                    away_manager_id = None
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
                        stadium_id,
                        referee_id,
                        home_manager_id,
                        away_manager_id,
                        match['season']['season_id']
                    )
                )


def create_tables(cursor: psycopg.cursor):
    # get file named createTables.sql
    with open('createTables.sql', 'r') as file:
        sql = file.read()
        cursor.execute(sql)


def drop_tables(cursor: psycopg.cursor):
    # get file named dropTables.sql
    with open('dropTables.sql', 'r') as file:
        sql = file.read()
        cursor.execute(sql)


def main():
    connection = psycopg.connect(
        host='localhost',
        dbname='PROJECT'
    )
    cursor = connection.cursor()

    data = get_relevant_data()

    drop_tables(cursor)
    create_tables(cursor)
    populate_from_competitions(cursor)
    populate_from_matches(cursor, data[3])
    # print(data[3][0])

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
