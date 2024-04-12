CREATE TABLE countries
(
    country_id   INT PRIMARY KEY,
    country_name VARCHAR(255)
);

CREATE TABLE body_part
(
    body_part_id   INT PRIMARY KEY,
    body_part_name VARCHAR(255)
);

CREATE TABLE season
(
    season_id      INT PRIMARY KEY,
    season_name    VARCHAR(255),
    competition_id INT
);

CREATE TABLE competition
(
    competition_id            INT,
    competition_name          VARCHAR(255),
    competition_gender        VARCHAR(50),
    competition_youth         BOOLEAN,
    competition_international BOOLEAN,
    season_id                 INT,
    country_name              VARCHAR(255),
    FOREIGN KEY (season_id) REFERENCES season (season_id)
);

CREATE TABLE team
(
    team_id     INT PRIMARY KEY,
    team_name   VARCHAR(255),
    team_gender VARCHAR(50),
    team_group  VARCHAR(50),
    country_id  INT,
    FOREIGN KEY (country_id) REFERENCES countries (country_id)
);

CREATE TABLE manager
(
    manager_id       INT PRIMARY KEY,
    manager_name     VARCHAR(255),
    manager_nickname VARCHAR(255),
    manager_dob      DATE,
    country_id       INT,
    FOREIGN KEY (country_id) REFERENCES countries (country_id)
);

CREATE TABLE referee
(
    referee_id   INT PRIMARY KEY,
    referee_name VARCHAR(255),
    country_id   INT,
    FOREIGN KEY (country_id) REFERENCES countries (country_id)
);

CREATE TABLE stadium
(
    stadium_id   INT PRIMARY KEY,
    stadium_name VARCHAR(255),
    country_id   INT,
    FOREIGN KEY (country_id) REFERENCES countries (country_id)
);

CREATE TABLE competition_stage
(
    competition_stage_id   INT PRIMARY KEY,
    competition_stage_name VARCHAR(255)
);

CREATE TABLE match
(
    match_id             INT PRIMARY KEY,
    match_date           DATE,
    kick_off             TIME,
    home_score           INT,
    away_score           INT,
    match_week           INT,
    competition_id       INT,
    home_team_id         INT,
    away_team_id         INT,
    competition_stage_id INT,
    stadium_id           INT,
    referee_id           INT,
    home_manager_id      INT,
    away_manager_id      INT,
    season_id            INT,
    FOREIGN KEY (season_id) REFERENCES season (season_id),
    FOREIGN KEY (home_team_id) REFERENCES team (team_id),
    FOREIGN KEY (away_team_id) REFERENCES team (team_id),
    FOREIGN KEY (competition_stage_id) REFERENCES competition_stage (competition_stage_id),
    FOREIGN KEY (stadium_id) REFERENCES stadium (stadium_id),
    FOREIGN KEY (referee_id) REFERENCES referee (referee_id),
    FOREIGN KEY (home_manager_id) REFERENCES manager (manager_id),
    FOREIGN KEY (away_manager_id) REFERENCES manager (manager_id)
);

CREATE TABLE player
(
    player_id       INT PRIMARY KEY,
    player_name     VARCHAR(255),
    player_nickname VARCHAR(255),
    jersey_number   INT,
    cards           VARCHAR(255),
    positions       VARCHAR(255),
    country_id      INT,
    FOREIGN KEY (country_id) REFERENCES countries (country_id)
);

CREATE TABLE position
(
    position_id   INT PRIMARY KEY,
    position_name VARCHAR(255)
);

CREATE TABLE play_pattern
(
    play_pattern_id   INT PRIMARY KEY,
    play_pattern_name VARCHAR(255)
);

CREATE TABLE player_position
(
    player_id    INT,
    position_id  INT,
    from_time    varchar(10),
    to_time      varchar(10),
    from_period  INT,
    to_period    INT,
    start_reason VARCHAR(50),
    end_reason   VARCHAR(50),
    PRIMARY KEY (player_id, position_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id),
    FOREIGN KEY (position_id) REFERENCES position (position_id)
);

CREATE TABLE event_type
(
    type_id   INT PRIMARY KEY,
    type_name VARCHAR(50)
);

CREATE TABLE pass_height
(
    height_id   INT PRIMARY KEY,
    height_name VARCHAR(50)
);

CREATE TABLE pass_body_part
(
    body_part_id   INT PRIMARY KEY,
    body_part_name VARCHAR(50)
);

CREATE TABLE pass_type
(
    pass_type_id INT PRIMARY KEY,
    pass_name    VARCHAR(50)
);

CREATE TABLE match_event
(
    event_id           uuid PRIMARY KEY,
    event_index        INT,
    period             INT,
    event_timestamp    varchar(50),
    minute             INT,
    second             INT,
    possession         INT,
    possession_team_id INT,
    play_pattern_id    INT,
    duration           DECIMAL(10, 3),
    event_type_id      INT,
    team_id            INT,
    player_id          INT,
    position_id        INT,
    match_id           INT,
    pass_id            INT,
    location_x         DECIMAL(10, 2),
    location_y         DECIMAL(10, 2),
    under_pressure     BOOLEAN,
    off_camera         BOOLEAN,
    out                BOOLEAN,
    related_events     uuid[],
    FOREIGN KEY (event_type_id) REFERENCES event_type (type_id),
    FOREIGN KEY (team_id) REFERENCES team (team_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id),
    FOREIGN KEY (position_id) REFERENCES position (position_id),
    FOREIGN KEY (match_id) REFERENCES match (match_id),
    FOREIGN KEY (pass_id) REFERENCES pass_type (pass_type_id),
    FOREIGN KEY (play_pattern_id) REFERENCES play_pattern (play_pattern_id)
);

CREATE TABLE pass
(
    pass_id           INT PRIMARY KEY,
    location_x        DECIMAL(10, 2),
    location_y        DECIMAL(10, 2),
    pass_duration     DECIMAL(10, 3),
    pass_length       DECIMAL(10, 2),
    pass_angle        DECIMAL(10, 2),
    pass_height_id    INT,
    pass_body_part_id INT,
    pass_type_id      INT,
    pass_location     VARCHAR(255),
    pass_recipient_id INT,
    event_id          uuid,
    FOREIGN KEY (pass_height_id) REFERENCES pass_height (height_id),
    FOREIGN KEY (pass_body_part_id) REFERENCES pass_body_part (body_part_id),
    FOREIGN KEY (pass_type_id) REFERENCES pass_type (pass_type_id),
    FOREIGN KEY (pass_recipient_id) REFERENCES player (player_id),
    FOREIGN KEY (event_id) REFERENCES match_event (event_id)
);

CREATE TABLE lineup
(
    team_id   INT,
    match_id  INT,
    player_id INT,
    FOREIGN KEY (team_id) REFERENCES team (team_id),
    FOREIGN KEY (match_id) REFERENCES match (match_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id)
);

CREATE TABLE tactics
(
    event_id  uuid,
    formation int,
    PRIMARY KEY (event_id),
    FOREIGN KEY (event_id) REFERENCES match_event (event_id)
);

CREATE TABLE lineup_player
(
    player_id     INT,
    position_id   INT,
    match_id      INT,
    FOREIGN KEY (player_id) REFERENCES player (player_id),
    FOREIGN KEY (position_id) REFERENCES position (position_id)
);

CREATE TABLE outcome
(
    outcome_id   INT PRIMARY KEY,
    outcome_name VARCHAR(255)
);

CREATE TABLE card
(
    card_id   INT PRIMARY KEY,
    card_name VARCHAR(25)
);

CREATE TABLE event_5050
(
    type_id      INT,
    event_id     uuid,
    outcome_id   INT,
    counterpress BOOLEAN,
    FOREIGN KEY (outcome_id) REFERENCES outcome (outcome_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_bad_behaviour
(
    event_id uuid,
    type_id  INT,
    card_id  INT,
    FOREIGN KEY (card_id) REFERENCES card (card_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_ball_receipt
(
    event_id   uuid,
    type_id    INT,
    outcome_id INT,
    FOREIGN KEY (outcome_id) REFERENCES outcome (outcome_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id),
    FOREIGN KEY (event_id) REFERENCES match_event (event_id)
);

CREATE TABLE event_ball_recovery
(
    type_id          INT,
    event_id         uuid,
    offensive        BOOLEAN,
    recovery_failure BOOLEAN,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_block
(
    type_id      INT,
    event_id     uuid,
    offensive    BOOLEAN,
    deflection   BOOLEAN,
    save_block   BOOLEAN,
    counterpress BOOLEAN,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_carry
(
    type_id        INT,
    event_id       uuid,
    end_location_x DECIMAL(10, 2),
    end_location_y DECIMAL(10, 2),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_clearance
(
    type_id      INT,
    event_id     uuid,
    aerial_won   BOOLEAN,
    body_part_id INT,
    FOREIGN KEY (body_part_id) REFERENCES pass_body_part (body_part_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_dribble
(
    type_id    INT,
    event_id   uuid,
    outcome_id INT,
    overrun    BOOLEAN,
    nutmeg     BOOLEAN,
    no_touch   BOOLEAN,
    FOREIGN KEY (outcome_id) REFERENCES outcome (outcome_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_dribbled_past
(
    type_id      INT,
    event_id     uuid,
    counterpress BOOLEAN,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE duel_type
(
    duel_type_id   INT PRIMARY KEY,
    event_id       uuid,
    duel_type_name VARCHAR(255)
);

CREATE TABLE event_duel
(
    type_id      INT,
    event_id     uuid,
    outcome_id   INT,
    duel_type_id INT,
    counterpress BOOLEAN,
    FOREIGN KEY (duel_type_id) REFERENCES duel_type (duel_type_id),
    FOREIGN KEY (outcome_id) REFERENCES outcome (outcome_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE foul_type
(
    foul_type_id   INT PRIMARY KEY,
    foul_type_name VARCHAR(255)
);

CREATE TABLE event_foul_committed
(
    type_id      INT,
    event_id     uuid,
    card_id      INT,
    counterpress BOOLEAN,
    offensive    BOOLEAN,
    advantage    BOOLEAN,
    penalty      BOOLEAN,
    foul_type_id INT,
    FOREIGN KEY (foul_type_id) REFERENCES foul_type (foul_type_id),
    FOREIGN KEY (card_id) REFERENCES card (card_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_foul_won
(
    type_id   INT,
    event_id  uuid,
    defensive BOOLEAN,
    advantage BOOLEAN,
    penalty   BOOLEAN,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE technique_type
(
    technique_type_id   INT PRIMARY KEY,
    technique_type_name VARCHAR(255)
);

CREATE TABLE goalkeeper_event_type
(
    goalkeeper_event_type_id   INT PRIMARY KEY,
    goalkeeper_event_type_name VARCHAR(255)
);

CREATE TABLE event_goalkeeper
(
    type_id                  INT,
    event_id                 uuid,
    position_id              INT,
    technique_id             INT,
    body_part_id             INT,
    goalkeeper_event_type_id INT,
    outcome_id               INT,
    FOREIGN KEY (goalkeeper_event_type_id) REFERENCES goalkeeper_event_type (goalkeeper_event_type_id),
    FOREIGN KEY (outcome_id) REFERENCES outcome (outcome_id),
    FOREIGN KEY (body_part_id) REFERENCES pass_body_part (body_part_id),
    FOREIGN KEY (technique_id) REFERENCES technique_type (technique_type_id),
    FOREIGN KEY (position_id) REFERENCES position (position_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_half_end
(
    type_id         INT,
    event_id        uuid,
    early_video_end BOOLEAN,
    match_suspended BOOLEAN,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_half_start
(
    type_id          INT,
    event_id         uuid,
    late_video_start BOOLEAN,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_injury_stoppage
(
    type_id  INT,
    event_id uuid,
    in_chain BOOLEAN,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_interception
(
    type_id    INT,
    event_id   uuid,
    outcome_id INT,
    FOREIGN KEY (outcome_id) references outcome (outcome_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_miscontrol
(
    type_id    INT,
    event_id   uuid,
    aerial_won BOOLEAN,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE recipient_type
(
    recipient_type_id   INT PRIMARY KEY,
    recipient_type_name VARCHAR(255)
);

CREATE TABLE event_pass_type
(
    type_id           INT,
    event_id          uuid,
    recipient_type_id INT,
    length            DECIMAL(10, 2),
    angle             DECIMAL(10, 2),
    height_id         INT,
    end_location_x    DECIMAL(10, 2),
    end_location_y    DECIMAL(10, 2),
    assisted_shot_id  uuid,
    backheel          BOOLEAN,
    deflected         BOOLEAN,
    miscommunication  BOOLEAN,
    "cross"           BOOLEAN,
    cutback           BOOLEAN,
    switch            BOOLEAN,
    shot_assist       BOOLEAN,
    goal_assist       BOOLEAN,
    body_part_id      INT,
    pass_type_id      INT,
    outcome_id        INT,
    technique_id      INT,
    FOREIGN KEY (recipient_type_id) REFERENCES recipient_type (recipient_type_id),
    FOREIGN KEY (height_id) REFERENCES pass_height (height_id),
    FOREIGN KEY (body_part_id) REFERENCES pass_body_part (body_part_id),
    FOREIGN KEY (pass_type_id) REFERENCES pass_type (pass_type_id),
    FOREIGN KEY (outcome_id) REFERENCES outcome (outcome_id),
    FOREIGN KEY (technique_id) REFERENCES technique_type (technique_type_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_player_off
(
    type_id   INT,
    permanent BOOLEAN,
    event_id  uuid,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE event_pressure
(
    type_id      INT,
    counterpress BOOLEAN,
    event_id     uuid,
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE location
(
    player_id INT,
    x         DECIMAL(10, 2),
    y         DECIMAL(10, 2)
);

CREATE TABLE freeze_frame_type
(
    freeze_frame_id uuid,
    location_id     INT,
    player_id       INT,
    position_id     INT,
    event_id        uuid,
    teammate        BOOLEAN,
    FOREIGN KEY (player_id) REFERENCES player (player_id),
    FOREIGN KEY (position_id) REFERENCES position (position_id)
);

CREATE TABLE shot_type
(
    shot_type_id   INT PRIMARY KEY,
    shot_type_name VARCHAR(255)
);

CREATE TABLE event_shot
(
    type_id         INT,
    event_id        uuid,
    key_pass_id     uuid,
    end_location_x  DECIMAL(10, 2),
    end_location_y  DECIMAL(10, 2),
    end_location_z  DECIMAL(10, 2),
    aerial_won      BOOLEAN,
    follows_dribble BOOLEAN,
    first_time      BOOLEAN,
    freeze_frame_id uuid,
    open_goal       BOOLEAN,
    statsbomb_xg    DECIMAL(10, 3),
    deflected       BOOLEAN,
    technique_id    INT,
    body_part_id    INT,
    shot_type_id    INT,
    outcome_id      INT,
    player_id       INT,
    FOREIGN KEY (player_id) REFERENCES player (player_id),
    FOREIGN KEY (technique_id) REFERENCES technique_type (technique_type_id),
    FOREIGN KEY (body_part_id) REFERENCES body_part (body_part_id),
    FOREIGN KEY (shot_type_id) REFERENCES shot_type (shot_type_id),
    FOREIGN KEY (outcome_id) REFERENCES outcome (outcome_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);

CREATE TABLE replacement_type
(
    replacement_type_id   INT PRIMARY KEY,
    replacement_type_name VARCHAR(255)
);

CREATE TABLE event_substitution
(
    type_id             INT,
    event_id            uuid,
    replacement_type_id INT,
    outcome_id          INT,
    FOREIGN KEY (replacement_type_id) REFERENCES replacement_type (replacement_type_id),
    FOREIGN KEY (outcome_id) REFERENCES outcome (outcome_id),
    FOREIGN KEY (type_id) REFERENCES event_type (type_id)
);