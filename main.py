import json
import psycopg
from typing import List


# Competition and seasons stored in competitions.json
# Matches for each competition and season, stored in matches. Each folder within is named for a competition ID,
# each file is named for a season ID within that competition.
def get_relevant_data() -> List:
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
def populate_from_matches(cursor: psycopg.cursor, match_file_paths: List) -> None:
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
def populate_from_events(cursor: psycopg.cursor, event_file_paths: List) -> None:
    event_types = {
        42: 'Ball Receipt',  #
        2: 'Ball Recovery',  #
        3: 'Dispossessed',  #
        4: 'Duel',  #
        5: 'Camera On',  #
        6: 'Block',  #
        8: 'Offside',  #
        9: 'Clearance',  #
        10: 'Interception',  #
        14: 'Dribble',  #
        16: 'Shot',  #
        17: 'Pressure',  #
        18: 'Half Start',  #
        19: 'Substitution',  #
        20: 'Own Goal Against',  #
        21: 'Foul Won',  #
        22: 'Foul Committed',  #
        23: 'Goal Keeper',  #
        24: 'Bad Behaviour',  #
        25: 'Own Goal For',  #
        26: 'Player On',  #
        27: 'Player Off',  #
        28: 'Shield',  #
        30: 'Pass',  #
        33: '50/50',  #
        34: 'Half End',  #
        35: 'Starting XI',  #
        36: 'Tactical Shift',  #
        37: 'Error',  #
        38: 'Miscontrol',
        39: 'Dribbled Past',
        40: 'Injury Stoppage',
        43: 'Carry'
    }

    count = 0
    for file in event_file_paths:
        count += 1
        print(f'populating from {file}. progress: {count}/{len(event_file_paths)}')
        with open(file) as f:
            data = json.load(f)
            for event in data:
                # print(f'current event: {event["id"]}')
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

                # insert into specific event table
                event_type_id = event['type']['id']
                if event_type_id == 42:
                    # Ball Receipt
                    cursor.execute(
                        'INSERT INTO event_ball_receipt (event_id, type_id, outcome_id)'
                        'VALUES (%s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('outcome', {}).get('id', None))
                    )

                elif event_type_id == 2:
                    cursor.execute(
                        'INSERT INTO event_ball_recovery (type_id, event_id, offensive, recovery_failure)'
                        'VALUES (%s, %s, %s, %s)',
                        (event['type']['id'], event['id'], event.get('offensive', None),
                         event.get('recovery_failure', None))
                    )

                elif event_type_id == 4:
                    # Duel
                    # check if duel type exists
                    cursor.execute('SELECT duel_type_id FROM duel_type WHERE duel_type_id = %s',
                                   (event['duel']['type']['id'],))
                    duel_type = cursor.fetchone()
                    if duel_type is None:
                        # add duel type to database
                        cursor.execute(
                            'INSERT INTO duel_type (duel_type_id, duel_type_name) VALUES (%s, %s)',
                            (event['duel']['type']['id'], event['duel']['type']['name'])
                        )

                    cursor.execute(
                        'INSERT INTO event_duel (event_id, type_id, outcome_id, duel_type_id)'
                        'VALUES (%s, %s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('outcome', {}).get('id', None),
                         event['duel']['type']['id'])
                    )

                elif event_type_id == 6:
                    # block
                    cursor.execute(
                        'INSERT INTO event_block (event_id, type_id, offensive, deflection, save_block, counterpress)'
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('offensive', None), event.get('deflection', None),
                         event.get('save_block', None), event.get('counterpress', None))
                    )

                elif event_type_id == 9:
                    # clearance
                    # check if body part exists
                    cursor.execute('SELECT body_part_id FROM body_part WHERE body_part_id = %s',
                                   (event['clearance']['body_part']['id'],))
                    body_part = cursor.fetchone()
                    if body_part is None:
                        # add body part to database
                        cursor.execute(
                            'INSERT INTO body_part (body_part_id, body_part_name) VALUES (%s, %s)',
                            (event['clearance']['body_part']['id'], event['clearance']['body_part']['name'])
                        )

                    cursor.execute(
                        'INSERT INTO event_clearance (event_id, type_id, aerial_won, body_part_id)'
                        'VALUES (%s, %s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('aerial_won', None),
                         event.get('body_part', {}).get('id', None))
                    )

                elif event_type_id == 10:
                    # interception
                    cursor.execute(
                        'INSERT INTO event_interception (event_id, type_id, outcome_id)'
                        'VALUES (%s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('outcome', {}).get('id', None))
                    )

                elif event_type_id == 14:
                    # dribble
                    cursor.execute(
                        'INSERT INTO event_dribble (event_id, type_id, outcome_id, nutmeg, overrun, no_touch)'
                        'VALUES (%s, %s, %s, %s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('outcome', {}).get('id', None),
                         event.get('nutmeg', None)
                         , event.get('overrun', None), event.get('no_touch', None))
                    )

                elif event_type_id == 16:
                    # shot
                    # check if shot type exists
                    cursor.execute('SELECT shot_type_id FROM shot_type WHERE shot_type_id = %s',
                                   (event['shot']['type']['id'],))
                    shot_type = cursor.fetchone()
                    if shot_type is None:
                        # add shot type to database
                        cursor.execute(
                            'INSERT INTO shot_type (shot_type_id, shot_type_name) VALUES (%s, %s)',
                            (event['shot']['type']['id'], event['shot']['type']['name'])
                        )

                    # check if shot technique exists
                    cursor.execute('SELECT technique_type_id FROM technique_type WHERE technique_type_id = %s',
                                   (event['shot']['technique']['id'],))
                    shot_technique = cursor.fetchone()
                    if shot_technique is None:
                        # add shot technique to database
                        cursor.execute(
                            'INSERT INTO technique_type (technique_type_id, technique_type_name) VALUES (%s, %s)',
                            (event['shot']['technique']['id'], event['shot']['technique']['name'])
                        )

                    # check if shot outcome exists
                    cursor.execute('SELECT outcome_id FROM outcome WHERE outcome_id = %s',
                                   (event['shot']['outcome']['id'],))
                    shot_outcome = cursor.fetchone()
                    if shot_outcome is None:
                        # add shot outcome to database
                        cursor.execute(
                            'INSERT INTO outcome (outcome_id, outcome_name) VALUES (%s, %s)',
                            (event['shot']['outcome']['id'], event['shot']['outcome']['name'])
                        )

                    # check if shot body part exists
                    cursor.execute('SELECT body_part_id FROM body_part WHERE body_part_id = %s',
                                   (event['shot']['body_part']['id'],))
                    shot_body_part = cursor.fetchone()
                    if shot_body_part is None:
                        # add shot body part to database
                        cursor.execute(
                            'INSERT INTO body_part (body_part_id, body_part_name) VALUES (%s, %s)',
                            (event['shot']['body_part']['id'], event['shot']['body_part']['name'])
                        )

                    ff = event['shot'].get('freeze_frame', None)

                    if ff is not None:

                        for i in ff:
                            # check if shot freeze frame player exists
                            cursor.execute('SELECT player_id FROM player WHERE player_id = %s',
                                           (i['player']['id'],))
                            player = cursor.fetchone()
                            if player is None:
                                # add player to database
                                cursor.execute(
                                    'INSERT INTO player (player_id, player_name) VALUES (%s, %s)',
                                    (i['player']['id'], i['player']['name'])
                                )

                            # check if shot freeze frame position exists
                            cursor.execute('SELECT position_id FROM position WHERE position_id = %s',
                                           (i['position']['id'],))
                            position = cursor.fetchone()
                            if position is None:
                                # add position to database
                                cursor.execute(
                                    'INSERT INTO position (position_id, position_name) VALUES (%s, %s)',
                                    (i['position']['id'], i['position']['name'])
                                )

                            cursor.execute(
                                'INSERT INTO location (player_id, x, y)'
                                'VALUES (%s, %s, %s)',
                                (i['player']['id'], i['location'][0], i['location'][1])
                            )

                            cursor.execute(
                                'INSERT INTO freeze_frame_type ( player_id, position_id, event_id, teammate) '
                                'VALUES (%s, %s, %s, %s)',
                                (i['player']['id'], i['position']['id'], event['id'],
                                 i.get('teammate', None))
                            )

                    key_pass_id = event['shot'].get('key_pass_id', None)
                    end_location = event['shot'].get('end_location', [None, None, None])
                    end_location_x = end_location[0]
                    end_location_y = end_location[1]
                    end_location_z = end_location[2] if len(end_location) == 3 else None
                    aerial_won = event['shot'].get('aerial_won', None)
                    follows_dribble = event['shot'].get('follows_dribble', None)
                    first_time = event['shot'].get('first_time', None)
                    freeze_frame_id = event['id']
                    open_goal = event['shot'].get('open_goal', None)
                    statsbomb_xg = event['shot'].get('statsbomb_xg', None)
                    deflected = event['shot'].get('deflected', None)

                    cursor.execute(
                        'INSERT INTO event_shot (event_id, type_id, outcome_id, technique_id, body_part_id, '
                        'freeze_frame_id, key_pass_id, end_location_x, end_location_y, end_location_z, aerial_won, '
                        'follows_dribble, first_time, open_goal, statsbomb_xg, deflected)'
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (event['id'], event['type']['id'], event['shot']['outcome']['id'],
                         event['shot']['technique']['id'],
                         event['shot']['body_part']['id'], freeze_frame_id, key_pass_id, end_location_x, end_location_y,
                         end_location_z, aerial_won, follows_dribble, first_time, open_goal, statsbomb_xg, deflected)
                    )

                elif event_type_id == 17:
                    # pressure
                    cursor.execute(
                        'INSERT INTO event_pressure (event_id, type_id, counterpress)'
                        'VALUES (%s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('counterpress', None))
                    )

                elif event_type_id == 18:
                    # half start
                    cursor.execute(
                        'INSERT INTO event_half_start (event_id, type_id, late_video_start)'
                        'VALUES (%s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('late_video_start', None))
                    )

                elif event_type_id == 19:
                    # substitution
                    # check if outcome exists
                    cursor.execute('SELECT outcome_id FROM outcome WHERE outcome_id = %s',
                                   (event['substitution']['outcome']['id'],))
                    outcome = cursor.fetchone()
                    if outcome is None:
                        # add outcome to database
                        cursor.execute(
                            'INSERT INTO outcome (outcome_id, outcome_name) VALUES (%s, %s)',
                            (event['substitution']['outcome']['id'], event['substitution']['outcome']['name'])
                        )

                    # check if player exists
                    cursor.execute('SELECT player_id FROM player WHERE player_id = %s',
                                   (event['substitution']['replacement']['id'],))
                    player = cursor.fetchone()
                    if player is None:
                        # add player to database
                        cursor.execute(
                            'INSERT INTO player (player_id, player_name) VALUES (%s, %s)',
                            (event['substitution']['replacement']['id'], event['substitution']['replacement']['name'])
                        )

                    # insert into replacement_type table
                    cursor.execute('SELECT replacement_type_id FROM replacement_type WHERE replacement_type_id = %s',
                                   (event['substitution']['replacement']['id'],))
                    replacement = cursor.fetchone()
                    if replacement is None:
                        cursor.execute(
                            'INSERT INTO replacement_type (replacement_type_id, replacement_type_name) VALUES (%s, %s)',
                            (event['substitution']['replacement']['id'], event['substitution']['replacement']['name'])
                        )

                    cursor.execute(
                        'INSERT INTO event_substitution (event_id, type_id, outcome_id, replacement_type_id)'
                        'VALUES (%s, %s, %s, %s)',
                        (event['id'], event['type']['id'], event['substitution']['outcome']['id'],
                         event['substitution']['replacement']['id'])
                    )

                elif event_type_id == 21:
                    # foul won
                    cursor.execute(
                        'INSERT INTO event_foul_won (event_id, type_id, defensive, advantage, penalty)'
                        'VALUES (%s, %s, %s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('foul_committed', None),
                         event.get('advantage', None), event.get('penalty', None))
                    )

                elif event_type_id == 22:
                    # foul committed
                    # check if card exists

                    # try catch
                    try:
                        c1 = event['foul_committed']['card']
                    except KeyError:
                        c1 = None

                    try:
                        c2 = event['foul_committed']['type']
                    except KeyError:
                        c2 = None

                    if c1 is not None:
                        cursor.execute('SELECT card_id FROM card WHERE card_id = %s',
                                       (event['foul_committed']['card']['id'],))
                        card = cursor.fetchone()
                        if card is None:
                            # add card to database
                            cursor.execute(
                                'INSERT INTO card (card_id, card_name) VALUES (%s, %s)',
                                (event['foul_committed']['card']['id'], event['foul_committed']['card']['name'])
                            )

                    if c2 is not None:
                        # check if foul type exists
                        cursor.execute('SELECT foul_type_id FROM foul_type WHERE foul_type_id = %s',
                                       (event['foul_committed']['type']['id'],))
                        foul = cursor.fetchone()
                        if foul is None:
                            # add foul to database
                            cursor.execute(
                                'INSERT INTO foul_type (foul_type_id, foul_type_name) VALUES (%s, %s)',
                                (event['foul_committed']['type']['id'], event['foul_committed']['type']['name'])
                            )

                    cursor.execute(
                        'INSERT INTO event_foul_committed (event_id, type_id, card_id, foul_type_id, advantage, '
                        'offensive, penalty, counterpress)'
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)',
                        (event['id'], event['type']['id'],
                         event.get('foul_committed', {}).get('card', {}).get('id', None),
                         event.get('foul_committed', {}).get('type', {}).get('id', None), event.get('advantage', None),
                         event.get('foul_committed', {}).get('offensive', None), event.get('penalty', None),
                         event.get('counterpress', None))
                    )

                elif event_type_id == 23:
                    # goalkeeper

                    try:
                        position_exists = event['goalkeeper']['position']['id']
                    except KeyError:
                        position_exists = None

                    if position_exists is not None:
                        # check if goalkeeper position exists
                        cursor.execute('SELECT position_id FROM position WHERE position_id = %s',
                                       (event['goalkeeper']['position']['id'],))
                        position = cursor.fetchone()
                        if position is None:
                            # add position to database
                            cursor.execute(
                                'INSERT INTO position (position_id, position_name) VALUES (%s, %s)',
                                (event['goalkeeper']['position']['id'],
                                 event['goalkeeper']['position']['name'])
                            )

                    try:
                        goalkeeper_type_exists = event['goalkeeper']['type']['id']
                    except KeyError:
                        goalkeeper_type_exists = None

                    if goalkeeper_type_exists is not None:

                        # check if goalkeeper type exists
                        cursor.execute('SELECT goalkeeper_event_type_id FROM goalkeeper_event_type WHERE '
                                       'goalkeeper_event_type_id = %s',
                                       (event['goalkeeper']['type']['id'],))
                        goalkeeper_type = cursor.fetchone()
                        if goalkeeper_type is None:
                            # add goalkeeper type to database
                            cursor.execute(
                                'INSERT INTO goalkeeper_event_type (goalkeeper_event_type_id ,'
                                'goalkeeper_event_type_name)'
                                'VALUES (%s, %s)',
                                (event['goalkeeper']['type']['id'], event['goalkeeper']['type']['name'])
                            )

                    try:
                        outcome_exists = event['goalkeeper']['outcome']['id']
                    except KeyError:
                        outcome_exists = None

                    if outcome_exists is not None:
                        # check if goalkeeper outcome exists
                        cursor.execute('SELECT outcome_id FROM outcome WHERE outcome_id = %s',
                                       (event['goalkeeper']['outcome']['id'],))
                        outcome = cursor.fetchone()
                        if outcome is None:
                            # add outcome to database
                            cursor.execute(
                                'INSERT INTO outcome (outcome_id, outcome_name) VALUES (%s, %s)',
                                (event['goalkeeper']['outcome']['id'], event['goalkeeper']['outcome']['name'])
                            )

                    # check if goalkeeper body part exists
                    try:
                        body_part_exists = event['goalkeeper']['body_part']['id']
                    except KeyError:
                        body_part_exists = None

                    if body_part_exists is not None:
                        cursor.execute('SELECT body_part_id FROM body_part WHERE body_part_id = %s',
                                       (event['goalkeeper']['body_part']['id'],))
                        body_part = cursor.fetchone()
                        if body_part is None:
                            # add body part to database
                            cursor.execute(
                                'INSERT INTO body_part (body_part_id, body_part_name) VALUES (%s, %s)',
                                (event['goalkeeper']['body_part']['id'], event['goalkeeper']['body_part']['name'])
                            )

                    cursor.execute(
                        'INSERT INTO event_goalkeeper (event_id, type_id, outcome_id, body_part_id, position_id, '
                        'technique_id, goalkeeper_event_type_id)'
                        'VALUES (%s, %s, %s, %s, %s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('outcome', {}).get('id', None),
                         event.get('body_part', {}).get('id', None), event.get('position', {}).get('id', None),
                         event.get('technique', {}).get('id', None),
                         event.get('goalkeeper', {}).get('type', {}).get('id', None))
                    )

                elif event_type_id == 24:
                    # bad behaviour
                    # check if card exists
                    cursor.execute('SELECT card_id FROM card WHERE card_id = %s',
                                   (event['bad_behaviour']['card']['id'],))
                    card = cursor.fetchone()
                    if card is None:
                        # add card to database
                        cursor.execute(
                            'INSERT INTO card (card_id, card_name) VALUES (%s, %s)',
                            (event['card']['id'], event['card']['name'])
                        )

                    cursor.execute(
                        'INSERT INTO event_bad_behaviour (event_id, type_id, card_id)'
                        'VALUES (%s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('card', {}).get('id', None))
                    )

                elif event_type_id == 30:
                    # pass

                    try:
                        recipient_exists = event['pass']['recipient']['id']
                    except KeyError:
                        recipient_exists = None

                    if recipient_exists is not None:
                        # check if recipient type exists
                        cursor.execute('SELECT recipient_type_id FROM recipient_type WHERE recipient_type_id = %s',
                                       (event['pass']['recipient']['id'],))
                        recipient_type = cursor.fetchone()
                        if recipient_type is None:
                            # add recipient type to database
                            cursor.execute(
                                'INSERT INTO recipient_type (recipient_type_id, recipient_type_name) VALUES (%s, %s)',
                                (event['pass']['recipient']['id'], event['pass']['recipient']['name'])
                            )

                    try:
                        height_exists = event['pass']['height']['id']
                    except KeyError:
                        height_exists = None

                    if height_exists is not None:
                        # check if pass height exists
                        cursor.execute('SELECT height_id FROM pass_height WHERE height_id = %s',
                                       (event['pass']['height']['id'],))
                        pass_height = cursor.fetchone()
                        if pass_height is None:
                            # add pass height to database
                            cursor.execute(
                                'INSERT INTO pass_height (height_id, height_name) VALUES (%s, %s)',
                                (event['pass']['height']['id'], event['pass']['height']['name'])
                            )

                    try:
                        body_part_exists = event['pass']['body_part']['id']
                    except KeyError:
                        body_part_exists = None

                    if body_part_exists is not None:
                        # check if pass body part exists
                        cursor.execute('SELECT body_part_id FROM body_part WHERE body_part_id = %s',
                                       (event['pass']['body_part']['id'],))
                        body_part = cursor.fetchone()
                        if body_part is None:
                            # add pass body part to database
                            cursor.execute(
                                'INSERT INTO body_part (body_part_id, body_part_name) VALUES (%s, %s)',
                                (event['pass']['body_part']['id'], event['pass']['body_part']['name'])
                            )
                        # do the same for pass_body_part
                        cursor.execute('SELECT body_part_id FROM pass_body_part WHERE body_part_id = %s',
                                        (event['pass']['body_part']['id'],))
                        pass_body_part = cursor.fetchone()
                        if pass_body_part is None:
                            cursor.execute(
                                'INSERT INTO pass_body_part (body_part_id, body_part_name) VALUES (%s, %s)',
                                (event['pass']['body_part']['id'], event['pass']['body_part']['name'])
                            )

                    try:
                        pass_type_exists = event['pass']['type']['id']
                    except KeyError:
                        pass_type_exists = None

                    if pass_type_exists:
                        cursor.execute('SELECT pass_type_id FROM pass_type WHERE pass_type_id = %s',
                                       (event['pass']['type']['id'],))
                        pass_type = cursor.fetchone()
                        if pass_type is None:
                            cursor.execute(
                                'INSERT INTO pass_type (pass_type_id, pass_name) VALUES (%s, %s)',
                                (event['pass']['type']['id'], event['pass']['type']['name'])
                            )

                    try:
                        outcome_exists = event['pass']['outcome']['id']
                    except KeyError:
                        outcome_exists = None

                    if outcome_exists:
                        cursor.execute('SELECT outcome_id FROM outcome WHERE outcome_id = %s',
                                       (event['pass']['outcome']['id'],))
                        outcome = cursor.fetchone()
                        if outcome is None:
                            cursor.execute(
                                'INSERT INTO outcome (outcome_id, outcome_name) VALUES (%s, %s)',
                                (event['pass']['outcome']['id'], event['pass']['outcome']['name'])
                            )

                    try:
                        technique_exists = event['pass']['technique']['id']
                    except KeyError:
                        technique_exists = None

                    if technique_exists:
                        cursor.execute('SELECT technique_type_id FROM technique_type WHERE technique_type_id = %s',
                                       (event['pass']['technique']['id'],))
                        technique = cursor.fetchone()
                        if technique is None:
                            cursor.execute(
                                'INSERT INTO technique_type (technique_type_id, technique_type_name) VALUES (%s, %s)',
                                (event['pass']['technique']['id'], event['pass']['technique']['name'])
                            )

                    try:
                        player_exists = event['pass']['recipient']['id']
                    except KeyError:
                        player_exists = None

                    if player_exists:
                        cursor.execute('SELECT player_id FROM player WHERE player_id = %s',
                                       (event['pass']['recipient']['id'],))
                        player = cursor.fetchone()
                        if player is None:
                            cursor.execute(
                                'INSERT INTO player (player_id, player_name) VALUES (%s, %s)',
                                (event['pass']['recipient']['id'], event['pass']['recipient']['name'])
                            )

                        # do the same for recipient type
                        cursor.execute('SELECT recipient_type_id FROM recipient_type WHERE recipient_type_id = %s',
                                       (event['pass']['recipient']['id'],))
                        recipient_type = cursor.fetchone()
                        if recipient_type is None:
                            cursor.execute(
                                'INSERT INTO recipient_type (recipient_type_id, recipient_type_name) VALUES (%s, %s)',
                                (event['pass']['recipient']['id'], event['pass']['recipient']['name'])
                            )

                    cursor.execute(
                        'INSERT INTO event_pass_type (type_id, event_id, recipient_type_id, length, angle, height_id, '
                        'end_location_x, end_location_y, assisted_shot_id, backheel, deflected, miscommunication, '
                        '"cross", cutback, switch, shot_assist, goal_assist, body_part_id, pass_type_id, outcome_id, '
                        'technique_id) '
                        'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '
                        '%s, %s, %s, %s, %s, %s, %s, %s, %s)',
                        (event.get('type', {}).get('id', None), event.get('id', None),
                         event.get('recipient', {}).get('id', None), event.get('length', None),
                         event.get('angle', None),
                         event.get('pass', {}).get('height', {}).get('id', None),
                         event.get('end_location', [None, None])[0], event.get('end_location', [None, None])[1],
                         event.get('assisted_shot_id', None), event.get('backheel', None), event.get('deflected', None),
                         event.get('miscommunication', None), event.get('cross', None), event.get('cutback', None),
                         event.get('switch', None), event.get('shot_assist', None), event.get('goal_assist', None),
                         event.get('pass', {}).get('body_part', {}).get('id', None),
                         event.get('pass', {}).get('type', {}).get('id', None),
                         event.get('pass', {}).get('outcome', {}).get('id', None),
                         event.get('pass', {}).get('technique', {}).get('id', None))
                    )

                elif event_type_id == 33:
                    # 50/50
                    cursor.execute(
                        'INSERT INTO event_5050 (event_id, type_id, outcome_id, counterpress)'
                        'VALUES (%s, %s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('outcome', {}).get('id', None),
                         event.get('counterpress', None))
                    )

                elif event_type_id == 34:
                    # half end
                    cursor.execute(
                        'INSERT INTO event_half_end (event_id, type_id, early_video_end, match_suspended)'
                        'VALUES (%s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('early_video_end', None),
                         event.get('match_suspended', None))
                    )

                elif event_type_id == 38:
                    # miscontrol
                    cursor.execute(
                        'INSERT INTO event_miscontrol (event_id, type_id, aerial_won)'
                        'VALUES (%s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('miscontrol', {}).get('aerial_won', None))
                    )

                elif event_type_id == 39:
                    # dribbled past
                    cursor.execute(
                        'INSERT INTO event_dribbled_past (event_id, type_id, counterpress)'
                        'VALUES (%s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('counterpress', {}).get('id', None))
                    )

                elif event_type_id == 40:
                    # injury stoppage
                    cursor.execute(
                        'INSERT INTO event_injury_stoppage (event_id, type_id, in_chain)'
                        'VALUES (%s, %s, %s)',
                        (event['id'], event['type']['id'], event.get('injury_stoppage', {}).get('in_chain', None))
                    )

                elif event_type_id == 43:
                    # carry
                    cursor.execute(
                        'INSERT INTO event_carry (type_id, event_id, end_location_x, end_location_y) '
                        'VALUES (%s, %s, %s, %s)',
                        (event.get('type', {}).get('id', None), event.get('id', None),
                         event.get('end_location', [None, None])[0], event.get('end_location', [None, None])[1])
                    )

                # todo if tactics field exists
                # there will be tactics object with
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
                    tactics = event['tactics']
                    formation = tactics.get('formation', None)
                    cursor.execute(
                        'INSERT INTO tactics (event_id, formation) VALUES (%s, %s)',
                        (event['id'], formation)
                    )

                    for lineup in tactics['lineup']:
                        player_id = lineup['player']['id']
                        position_id = lineup['position']['id']
                        jersey_number = lineup.get('jersey_number', None)

                        cursor.execute('SELECT player_id FROM player WHERE player_id = %s', (player_id,))
                        player = cursor.fetchone()
                        if player is None:
                            cursor.execute(
                                'INSERT INTO player (player_id, player_name, jersey_number) VALUES (%s, %s, %s)',
                                (player_id, lineup['player']['name'], jersey_number)
                            )

                        cursor.execute('SELECT position_id FROM position WHERE position_id = %s', (position_id,))
                        position = cursor.fetchone()
                        if position is None:
                            cursor.execute(
                                'INSERT INTO position (position_id, position_name) VALUES (%s, %s)',
                                (position_id, lineup['position']['name'])
                            )

                        match_id = file.split('/')[-1].split('.')[0]
                        cursor.execute(
                            'INSERT INTO lineup (team_id, match_id, player_id) '
                            'VALUES (%s, %s, %s)',
                            (event['team']['id'], match_id, player_id)
                        )
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
