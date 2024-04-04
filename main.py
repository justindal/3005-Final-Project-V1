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
    print('populating from competitions.json')
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
    print('done')


# data from matches folder
def populate_from_matches(cursor: psycopg.cursor, match_file_paths: []) -> None:
    print('populating from matches folder')
    for file in match_file_paths:
        with open(file) as f:
            data = json.load(f)
            for match in data:
                # print(f'match: {match["match_id"]} and file: {file}')
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
                                'INSERT INTO manager'
                                '(manager_id, manager_name, country_id, manager_dob, manager_nickname)'
                                'VALUES (%s, %s, %s, %s, %s)',
                                (manager['id'], manager['name'], manager['country']['id'], manager['dob'],
                                 manager['nickname'])
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
                                'INSERT INTO manager '
                                '(manager_id, manager_name, country_id, manager_dob, manager_nickname) '
                                'VALUES (%s, %s, %s, %s, %s)',
                                (manager['id'], manager['name'], manager['country']['id'], manager['dob'],
                                 manager['nickname'])
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
    print('done')


# populate from events folder TODO
def populate_from_events(cursor: psycopg.cursor, event_file_paths: []) -> None:
    for file in event_file_paths:
        print(f'populating from {file}')
        with open(file) as f:
            data = json.load(f)
            for event in data:
                # check if event type exists
                cursor.execute('SELECT type_id FROM event_type WHERE type_id = %s',
                               (event['type']['id'],))
                event_type = cursor.fetchone()
                if event_type is None:
                    # add event type to database
                    cursor.execute(
                        'INSERT INTO event_type (type_id, type_name) VALUES (%s, %s)',
                        (event['type']['id'], event['type']['name'])
                    )

                # check if play pattern exists
                cursor.execute('SELECT play_pattern_id FROM play_pattern WHERE play_pattern_id = %s',
                               (event['play_pattern']['id'],))
                play_pattern = cursor.fetchone()
                if play_pattern is None:
                    # add play pattern to database
                    cursor.execute(
                        'INSERT INTO play_pattern (play_pattern_id, play_pattern_name) VALUES (%s, %s)',
                        (event['play_pattern']['id'], event['play_pattern']['name'])
                    )

                # load event data

                # first load basic event data:
                # id, index, period, timestamp, minute, second, type_id, play_pattern_id, team_id,
                # possession, possession_team_id, duration
                cursor.execute(
                    'INSERT INTO match_event (event_id, event_index, period, event_timestamp, minute, second, '
                    'event_type_id, play_pattern_id, team_id, possession, possession_team_id, duration, '
                    'under_pressure, off_camera, out )'
                    'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                    (event['id'], event['index'], event['period'], event['timestamp'], event['minute'],
                     event['second'], event['type']['id'], event['play_pattern']['id'], event['team']['id'],
                     event['possession'], event['possession_team']['id'], event.get('duration', None),
                     event.get('under_pressure', None), event.get('off_camera', None), event.get('out', None)
                     )
                )

                # if tactics field exists, there will be tactics object with
                # int formation
                # lineups: An array of objects, each representing a player in the starting lineup.
                # Each object in the lineup:
                # player: An object with id and name for the player
                # position: An object with id and name for the player's position
                # jersey_number: The player's jersey number

                # if it doesn't exist, instead
                # player: An object with id and name for the player
                # position: An object with id and name for the player's position
                # location: An object with x and y coordinates for the location of the event
                # related_events: An array of objects, each representing an event that is related to the event.

                if 'tactics' in event:
                    pass
                else:
                    event_id = event['id']
                    player_id = event.get('player', {}).get('id', None)
                    position_id = event.get('position', {}).get('id', None)
                    location = event.get('location', [None, None])
                    location_x = location[0]
                    location_y = location[1]
                    related_events = event.get('related_events', None)

                    if player_id is not None:
                        cursor.execute('SELECT player_id FROM player WHERE player_id = %s', (player_id,))
                        player = cursor.fetchone()
                        if player is None:
                            cursor.execute(
                                'INSERT INTO player (player_id, player_name) VALUES (%s, %s)',
                                (player_id, event.get('player', {}).get('name', None))
                            )

                    if position_id is not None:
                        cursor.execute('SELECT position_id FROM position WHERE position_id = %s', (position_id,))
                        position = cursor.fetchone()
                        if position is None:
                            cursor.execute(
                                'INSERT INTO position (position_id, position_name) VALUES (%s, %s)',
                                (position_id, event.get('position', {}).get('name', None))
                            )

                    cursor.execute(
                        'UPDATE match_event '
                        'SET player_id = %s, position_id = %s, location_x = %s, location_y = %s, related_events = %s '
                        'WHERE event_id = %s',
                        (player_id, position_id, location_x, location_y, related_events, event_id)
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

    # competition_ids, season_ids, match_ids, match_file_paths, event_file_paths, lineup_file_paths
    data = get_relevant_data()

    drop_tables(cursor)
    create_tables(cursor)
    populate_from_competitions(cursor)
    populate_from_matches(cursor, data[3])
    populate_from_events(cursor, data[4])

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == '__main__':
    main()
