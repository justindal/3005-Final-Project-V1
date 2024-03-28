-- Create countries table
CREATE TABLE countries (
  country_id INT PRIMARY KEY,
  country_name VARCHAR(255)
);

-- Create teams table
CREATE TABLE teams (
  team_id INT PRIMARY KEY,
  team_name VARCHAR(255),
  country_id INT,
  team_gender VARCHAR(255),
  team_group VARCHAR(255),
  FOREIGN KEY (country_id) REFERENCES countries(country_id)
);

-- Create players table
CREATE TABLE players (
  player_id INT PRIMARY KEY,
  player_name VARCHAR(255),
  player_nickname VARCHAR(255),
  country_id INT,
  date_of_birth DATE,
  FOREIGN KEY (country_id) REFERENCES countries(country_id)
);

-- Create positions table
CREATE TABLE positions (
  position_id INT PRIMARY KEY,
  position_name VARCHAR(255)
);

-- Create player_positions table
CREATE TABLE player_positions (
  player_id INT,
  position_id INT,
  start_date DATE,
  end_date DATE,
  FOREIGN KEY (player_id) REFERENCES players(player_id),
  FOREIGN KEY (position_id) REFERENCES positions(position_id)
);

-- Create stadiums table
CREATE TABLE stadiums (
  stadium_id INT PRIMARY KEY,
  stadium_name VARCHAR(255),
  country_id INT,
  FOREIGN KEY (country_id) REFERENCES countries(country_id)
);

-- Create referees table
CREATE TABLE referees (
  referee_id INT PRIMARY KEY,
  referee_name VARCHAR(255),
  country_id INT,
  FOREIGN KEY (country_id) REFERENCES countries(country_id)
);

-- Create competition_stages table
CREATE TABLE competition_stages (
  stage_id INT PRIMARY KEY,
  stage_name VARCHAR(255)
);

-- Create competitions table
CREATE TABLE competitions (
  competition_id INT PRIMARY KEY,
  season_id INT,
  country_id INT,
  competition_name VARCHAR(255),
  competition_gender VARCHAR(255),
  competition_youth BOOLEAN,
  competition_international BOOLEAN,
  season_name VARCHAR(255),
  FOREIGN KEY (country_id) REFERENCES countries(country_id)
);

-- Create matches table
CREATE TABLE matches (
  match_id INT PRIMARY KEY,
  competition_id INT,
  season_id INT,
  match_date DATE,
  kick_off TIME,
  match_week INT,
  competition_stage_id INT,
  stadium_id INT,
  referee_id INT,
  home_team_id INT,
  away_team_id INT,
  home_score INT,
  away_score INT,
  match_status VARCHAR(255),
  FOREIGN KEY (competition_id) REFERENCES competitions(competition_id),
  FOREIGN KEY (competition_stage_id) REFERENCES competition_stages(stage_id),
  FOREIGN KEY (stadium_id) REFERENCES stadiums(stadium_id),
  FOREIGN KEY (referee_id) REFERENCES referees(referee_id),
  FOREIGN KEY (home_team_id) REFERENCES teams(team_id),
  FOREIGN KEY (away_team_id) REFERENCES teams(team_id)
);

-- Create event_types table
CREATE TABLE event_types (
  type_id INT PRIMARY KEY,
  type_name VARCHAR(255)
);

-- Create play_patterns table
CREATE TABLE play_patterns (
  play_pattern_id INT PRIMARY KEY,
  play_pattern_name VARCHAR(255)
);

-- Create events table
CREATE TABLE events (
  event_id INT PRIMARY KEY,
  match_id INT,
  event_type_id INT,
  period INT,
  timestamp TIME,
  minute INT,
  second INT,
  possession INT,
  possession_team_id INT,
  play_pattern_id INT,
  team_id INT,
  player_id INT,
  position_id INT,
  duration FLOAT,
  FOREIGN KEY (match_id) REFERENCES matches(match_id),
  FOREIGN KEY (event_type_id) REFERENCES event_types(type_id),
  FOREIGN KEY (possession_team_id) REFERENCES teams(team_id),
  FOREIGN KEY (play_pattern_id) REFERENCES play_patterns(play_pattern_id),
  FOREIGN KEY (team_id) REFERENCES teams(team_id),
  FOREIGN KEY (player_id) REFERENCES players(player_id),
  FOREIGN KEY (position_id) REFERENCES positions(position_id)
);

-- Create event-specific tables (example: passes table)
CREATE TABLE passes (
  pass_id INT PRIMARY KEY,
  event_id INT,
  pass_type VARCHAR(255),
  pass_outcome VARCHAR(255),
  FOREIGN KEY (event_id) REFERENCES events(event_id)
);

-- Create match_lineups table
CREATE TABLE match_lineups (
  lineup_id INT PRIMARY KEY,
  match_id INT,
  player_id INT,
  position_id INT,
  start_time TIME,
  end_time TIME,
  FOREIGN KEY (match_id) REFERENCES matches(match_id),
  FOREIGN KEY (player_id) REFERENCES players(player_id),
  FOREIGN KEY (position_id) REFERENCES positions(position_id)
);

-- Create team_competitions table
CREATE TABLE team_competitions (
  team_id INT,
  competition_id INT,
  season_id INT,
  FOREIGN KEY (team_id) REFERENCES teams(team_id),
  FOREIGN KEY (competition_id) REFERENCES competitions(competition_id)
);
