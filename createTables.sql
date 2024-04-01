CREATE TABLE countries
(
    country_id   INT PRIMARY KEY,
    country_name VARCHAR(255)
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

CREATE TABLE player_position
(
    player_id    INT,
    position_id  INT,
    from_time    TIME,
    to_time      TIME,
    from_period  VARCHAR(50),
    to_period    VARCHAR(50),
    start_reason VARCHAR(255),
    end_reason   VARCHAR(255),
    PRIMARY KEY (player_id, position_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id),
    FOREIGN KEY (position_id) REFERENCES position (position_id)
);

CREATE TABLE event_type
(
    type_id   INT PRIMARY KEY,
    type_name VARCHAR(255)
);

CREATE TABLE pass_height
(
    height_id   INT PRIMARY KEY,
    height_name VARCHAR(255)
);

CREATE TABLE pass_body_part
(
    body_part_id   INT PRIMARY KEY,
    body_part_name VARCHAR(255)
);

CREATE TABLE pass_type
(
    pass_type_id INT PRIMARY KEY,
    pass_name    VARCHAR(255)
);

CREATE TABLE match_event
(
    event_id        INT PRIMARY KEY,
    event_index     INT,
    period          INT,
    event_timestamp TIME,
    minute          INT,
    second          INT,
    possession      INT,
    duration        DECIMAL(10, 2),
    event_type_id   INT,
    team_id         INT,
    player_id       INT,
    position_id     INT,
    match_id        INT,
    pass_id         INT,
    FOREIGN KEY (event_type_id) REFERENCES event_type (type_id),
    FOREIGN KEY (team_id) REFERENCES team (team_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id),
    FOREIGN KEY (position_id) REFERENCES position (position_id),
    FOREIGN KEY (match_id) REFERENCES match (match_id)
);

CREATE TABLE pass
(
    pass_id           INT PRIMARY KEY,
    location_x        DECIMAL(10, 2),
    location_y        DECIMAL(10, 2),
    pass_duration     DECIMAL(10, 2),
    pass_length       DECIMAL(10, 2),
    pass_angle        DECIMAL(10, 2),
    pass_height_id    INT,
    pass_body_part_id INT,
    pass_type_id      INT,
    pass_location     VARCHAR(255),
    pass_recipient_id INT,
    event_id          INT,
    FOREIGN KEY (pass_height_id) REFERENCES pass_height (height_id),
    FOREIGN KEY (pass_body_part_id) REFERENCES pass_body_part (body_part_id),
    FOREIGN KEY (pass_type_id) REFERENCES pass_type (pass_type_id),
    FOREIGN KEY (pass_recipient_id) REFERENCES player (player_id),
    FOREIGN KEY (event_id) REFERENCES match_event (event_id)
);

CREATE TABLE play_pattern
(
    play_pattern_id   INT PRIMARY KEY,
    play_pattern_name VARCHAR(255)
);

CREATE TABLE lineup
(
    lineup_id INT PRIMARY KEY,
    team_id   INT,
    match_id  INT,
    player_id INT,
    FOREIGN KEY (team_id) REFERENCES team (team_id),
    FOREIGN KEY (match_id) REFERENCES match (match_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id)
);

CREATE TABLE tactics
(
    event_id  INT,
    formation VARCHAR(255),
    PRIMARY KEY (event_id),
    FOREIGN KEY (event_id) REFERENCES match_event (event_id)
);

CREATE TABLE lineup_player
(
    lineup_id INT,
    player_id INT,
    PRIMARY KEY (lineup_id, player_id),
    FOREIGN KEY (lineup_id) REFERENCES lineup (lineup_id),
    FOREIGN KEY (player_id) REFERENCES player (player_id)
);