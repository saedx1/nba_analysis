"""
This module holds the nba data fetching functions.
It either fetches them from the nba_api or the local storage.
"""
import os
from pathlib import Path
from typing import List

import pandas as pd
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import (
    TeamGameLog,
    TeamDashPtShots,
    TeamDashPtPass,
    TeamDashPtReb,
    PlayerCareerStats,
    BoxScoreTraditionalV2,
    BoxScoreFourFactorsV2,
    BoxScoreAdvancedV2,
    BoxScoreUsageV2,
    BoxScorePlayerTrackV2,
    BoxScoreScoringV2,
    BoxScoreDefensive,
    BoxScoreMatchups,
    BoxScoreMiscV2,
)

DATA_DIR = Path(
    os.environ["NBA_DATA_DIR"] if "NBA_DATA_DIR" in os.environ.keys() else "nba_data"
)


def get_dataframe(filename: str) -> pd.DataFrame:
    """
    Checks if a file of the dataframe exists and returns it.
    """
    path = Path(DATA_DIR / filename)
    if path.exists():
        return pd.read_parquet(path)

    return None


def save_dataframe(dataframe: pd.DataFrame, filename: str) -> None:
    """
    Stores a dataframe in a parquet file.
    """
    path = Path(DATA_DIR / filename)
    dataframe.to_parquet(path, engine="pyarrow", version="2.0", compression="zstd")


def get_teams() -> pd.DataFrame:
    """
    Get nba teams in a dataframe.
    """
    filename = "nba_teams.parquet"
    nba_teams = get_dataframe(filename)
    if nba_teams is None:
        nba_teams = teams.get_teams()
        nba_teams = {i["abbreviation"]: i for i in nba_teams}
        nba_teams = pd.DataFrame(nba_teams).T
        save_dataframe(nba_teams, "nba_teams.parquet")

    return nba_teams


def get_players(is_active: bool = False) -> pd.DataFrame:
    """
    Get nba players in a dataframe.
    """
    filename = "nba_players.parquet"
    nba_players = get_dataframe(filename)
    if nba_players is None:
        nba_players = players.get_players()
        nba_players = {i["full_name"]: i for i in nba_players}
        nba_players = pd.DataFrame(nba_players).T
        save_dataframe(nba_players, filename)

    if is_active:
        nba_players = nba_players[nba_players["is_active"]]

    return nba_players


def get_season(
    team_id: str, season: str, invalidate: bool = False, **kwargs
) -> pd.DataFrame:
    """
    Get nba season for an nba team.
    """
    filename = f"{team_id}_{season}.parquet"
    if not invalidate:
        team_season = get_dataframe(filename)
        if team_season is None:
            invalidate = True

    if invalidate:
        team_season = TeamGameLog(team_id, season, **kwargs).get_data_frames()[0]
        save_dataframe(team_season, filename)

    return team_season


def get_shots(**kwargs) -> pd.DataFrame:
    team_shots = TeamDashPtShots(**kwargs).get_data_frames()[0].iloc[:, 2:]
    return team_shots


def get_passes(**kwargs) -> pd.DataFrame:
    team_shots = TeamDashPtPass(**kwargs).get_data_frames()[0].iloc[:, 2:]
    return team_shots


def get_rebounds(**kwargs) -> pd.DataFrame:
    team_shots = TeamDashPtReb(**kwargs).get_data_frames()[0].iloc[:, 2:]
    return team_shots


class NBATeam:
    """
    A class that represents an NBA Team.
    """

    CURRENT_SEASON = "2019-20"

    @staticmethod
    def get_teams_list():
        nba_teams = get_teams()
        teams_list = [NBATeam(row.full_name, row.id) for _, row in nba_teams.iterrows()]
        return teams_list

    def __init__(self, name: str, team_id: str):
        self._name = name
        self._team_id = team_id
        self._players = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def team_id(self) -> str:
        return self._team_id

    @property
    def players(self) -> list:
        return self._players

    @players.setter
    def set_players(self, player_list: list):
        self._players = player_list

    def get_season(
        self, season: str = None, invalidate: bool = False, **kwargs
    ) -> pd.DataFrame:
        """
        Gets team's matches for a whole season.
        """
        if season is None:
            season = NBATeam.CURRENT_SEASON

        return get_season(
            team_id=self.team_id, season=season, invalidate=invalidate, **kwargs
        )

    def get_last_matches(self, last_n_games: int, **kwargs) -> pd.DataFrame:
        """
        Get's last n games for a team in this season.
        """
        return self.get_season(invalidate=True, **kwargs).iloc[:last_n_games]

    def get_shots(
        self, last_n_games: int = 0, season: str = None, **kwargs
    ) -> pd.DataFrame:
        """
        Gets detailed team shots over the course of a season or last n games.
        """
        if season is None:
            season = NBATeam.CURRENT_SEASON

        return get_shots(
            team_id=self.team_id, last_n_games=last_n_games, season=season, **kwargs
        )

    def get_passes(
        self, last_n_games: int = 0, season: str = None, **kwargs
    ) -> pd.DataFrame:
        """
        Gets detailed team passes per player over the course of a season or last n games.
        """
        if season is None:
            season = NBATeam.CURRENT_SEASON

        return get_passes(
            team_id=self.team_id, last_n_games=last_n_games, season=season, **kwargs
        )

    def get_rebounds(
        self, last_n_games: int = 0, season: str = None, **kwargs
    ) -> pd.DataFrame:
        """
        Gets detailed team rebounds over the course of a season or last n games.
        """
        if season is None:
            season = NBATeam.CURRENT_SEASON

        return get_rebounds(
            team_id=self.team_id, last_n_games=last_n_games, season=season, **kwargs
        )

    def __repr__(self):
        return f"<{self.__class__.__name__}_id={self.team_id}_name={self.name}>"


class NBAPlayer:
    """
    A class that represents an NBA player
    """

    @staticmethod
    def get_players_list(is_active: bool = False):
        nba_players = get_players(is_active)
        players_list = [
            NBAPlayer(row.full_name, row.id) for _, row in nba_players.iterrows()
        ]
        return players_list

    def __init__(self, name: str, player_id: str):
        self._name = name
        self._player_id = player_id

    @property
    def name(self) -> str:
        return self._name

    @property
    def player_id(self) -> str:
        return self._player_id

    def get_careet_stats(
        self, season_list: List[str] = None, team_id_list: List[str] = None, **kwargs
    ) -> pd.DataFrame:
        career = PlayerCareerStats(
            player_id=self.player_id, **kwargs
        ).get_data_frames()[0]
        if season_list:
            career = career[career["SEASON_ID"].isin(season_list)]

        if team_id_list:
            career = career[career["TEAM_ID"].astype("str").isin(team_id_list)]

        return career

    def __repr__(self):
        return f"<{self.__class__.__name__}_id={self.player_id}_name={self.name}>"


class NBAGame:
    def __init__(self, game_id):
        self._game_id = game_id

    @property
    def game_id(self):
        return self._game_id

    def get_traditional_stats(self, **kwargs):
        stats = BoxScoreTraditionalV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    def get_fourfactors_stats(self, **kwargs):
        stats = BoxScoreFourFactorsV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    def get_advanced_stats(self, **kwargs):
        stats = BoxScoreAdvancedV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    def get_usage_stats(self, **kwargs):
        stats = BoxScoreUsageV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    def get_playertrack_stats(self, **kwargs):
        stats = BoxScorePlayerTrackV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    def get_scoring_stats(self, **kwargs):
        stats = BoxScoreScoringV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    def get_matchup_stats(self, **kwargs):
        stats = BoxScoreMatchups(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    def get_defensive_stats(self, **kwargs):
        stats = BoxScoreDefensive(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    def get_misc_stats(self, **kwargs):
        stats = BoxScoreMiscV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats
