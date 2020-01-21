"""
This module holds the nba data fetching functions.
It either fetches them from the nba_api or the local storage.
"""
from pathlib import Path
from typing import List
from functools import lru_cache

import pandas as pd
from cached_property import cached_property
import nba_api.stats.library.data as nba_static_data
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
    ShotChartDetail,
    PlayerProfileV2,
    PlayerDashPtShots,
)

CURRENT_SEASON = "2019-20"


def get_dataframe(filename: str) -> pd.DataFrame:
    """
    Checks if a file of the dataframe exists and returns it.
    """
    path = Path(filename)
    if path.exists():
        return pd.read_parquet(path)

    return None


def save_dataframe(dataframe: pd.DataFrame, filename: str) -> None:
    """
    Stores a dataframe in a parquet file.
    """
    path = Path(filename)
    dataframe.to_parquet(path, engine="pyarrow", version="2.0", compression="zstd")


def get_season(team_id: str, season: str, **kwargs) -> pd.DataFrame:
    """
    Get nba season for an nba team.
    """
    team_season = TeamGameLog(team_id, season, **kwargs).get_data_frames()[0]
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

    @staticmethod
    @lru_cache(maxsize=1)
    def get_teams_list():
        nba_teams = nba_static_data.teams
        teams_list = {team[1]: NBATeam(team[1], team[5], team[0]) for team in nba_teams}
        return teams_list

    def __init__(self, abbreviation: str, full_name: str, team_id: str):
        self._abbreviation = abbreviation
        self._full_name = full_name
        self._team_id = team_id
        self._players = None

    @property
    def abbreviation(self) -> str:
        return self._abbreviation

    @property
    def full_name(self) -> str:
        return self._full_name

    @property
    def team_id(self) -> str:
        return self._team_id

    @property
    def players(self) -> list:
        return self._players

    @players.setter
    def set_players(self, player_list: list):
        self._players = player_list

    def get_season(self, season: str = CURRENT_SEASON, **kwargs) -> pd.DataFrame:
        """
        Gets team's matches for a whole season.
        """
        return get_season(team_id=self.team_id, season=season, **kwargs)

    @lru_cache(maxsize=128)
    def get_last_matches(self, last_n_games: int = None, **kwargs) -> pd.DataFrame:
        """
        Get's last n games for a team in this season.
        """

        season = self.get_season(**kwargs)
        if last_n_games:
            season = season.iloc[:last_n_games]

        return season

    def get_shots(
        self, last_n_games: int = 0, season: str = CURRENT_SEASON, **kwargs
    ) -> pd.DataFrame:
        """
        Gets detailed team shots over the course of a season or last n games.
        """

        return get_shots(
            team_id=self.team_id, last_n_games=last_n_games, season=season, **kwargs
        )

    def get_passes(
        self, last_n_games: int = 0, season: str = CURRENT_SEASON, **kwargs
    ) -> pd.DataFrame:
        """
        Gets detailed team passes per player over the course of a season or last n games.
        """

        return get_passes(
            team_id=self.team_id, last_n_games=last_n_games, season=season, **kwargs
        )

    def get_rebounds(
        self, last_n_games: int = 0, season: str = CURRENT_SEASON, **kwargs
    ) -> pd.DataFrame:
        """
        Gets detailed team rebounds over the course of a season or last n games.
        """

        return get_rebounds(
            team_id=self.team_id, last_n_games=last_n_games, season=season, **kwargs
        )

    def __repr__(self):
        return f"<{self.__class__.__name__}_id={self.team_id}_name={self.full_name}>"


class NBAPlayer:
    """
    A class that represents an NBA player
    """

    @staticmethod
    def get_players_list(is_active: bool = False):
        nba_players = nba_static_data.players
        players_list = {
            player[3]: NBAPlayer(player[3], player[0])
            for player in nba_players
            if not is_active or player[4]
        }

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

    @cached_property
    def current_team(self):
        profile = PlayerProfileV2(self.player_id).get_data_frames()
        abbreviation = profile[0].loc[:, "TEAM_ABBREVIATION"].values[-1]
        team_id = NBATeam.get_teams_list()[abbreviation].team_id
        return team_id

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

    @lru_cache(maxsize=10)
    def _get_shots(
        self,
        team_id: str,
        last_n_games: int,
        season: str,
        opponent_team_id: str,
        **kwargs,
    ):

        if team_id == "current":
            team_id = self.current_team

        shots = PlayerDashPtShots(
            team_id,
            self.player_id,
            last_n_games,
            season=season,
            opponent_team_id=opponent_team_id,
            **kwargs,
        ).get_data_frames()

        return shots

    def get_shot_details(
        self,
        team_id: str = "current",
        last_n_games: int = 0,
        season: str = CURRENT_SEASON,
        made_miss: bool = True,
        opponent_team_id: str = 0,
        game_id: str = None,
        **kwargs,
    ) -> pd.DataFrame:

        if team_id == "current":
            team_id = self.current_team

        context = "PTS"
        if not made_miss:
            context = "FGA"

        shots = ShotChartDetail(
            team_id,
            self.player_id,
            last_n_games=last_n_games,
            season_nullable=season,
            context_measure_simple=context,
            opponent_team_id=opponent_team_id,
            **kwargs,
        ).get_data_frames()[0]

        if game_id:
            shots = shots[shots["GAME_ID"] == game_id]

        return shots

    def get_shots_overall(
        self,
        team_id: str = "current",
        last_n_games: int = 0,
        season: str = CURRENT_SEASON,
        opponent_team_id: str = 0,
        **kwargs,
    ):
        shots = self._get_shots(
            team_id, last_n_games, season, opponent_team_id, **kwargs
        )[0]
        return shots

    def get_shots_per_type(
        self,
        team_id: str = "current",
        last_n_games: int = 0,
        season: str = CURRENT_SEASON,
        opponent_team_id: str = 0,
        **kwargs,
    ):
        shots = self._get_shots(
            team_id, last_n_games, season, opponent_team_id, **kwargs
        )[1]
        return shots

    def get_shots_per_shotclock(
        self,
        team_id: str = "current",
        last_n_games: int = 0,
        season: str = CURRENT_SEASON,
        opponent_team_id: str = 0,
        **kwargs,
    ):
        shots = self._get_shots(
            team_id, last_n_games, season, opponent_team_id, **kwargs
        )[2]
        return shots

    def get_shots_per_dribble(
        self,
        team_id: str = "current",
        last_n_games: int = 0,
        season: str = CURRENT_SEASON,
        opponent_team_id: str = 0,
        **kwargs,
    ):
        shots = self._get_shots(
            team_id, last_n_games, season, opponent_team_id, **kwargs
        )[3]
        return shots

    def get_shots_per_distance_from_defender(
        self,
        team_id: str = "current",
        last_n_games: int = 0,
        season: str = CURRENT_SEASON,
        opponent_team_id: str = 0,
        **kwargs,
    ):
        shots = self._get_shots(
            team_id, last_n_games, season, opponent_team_id, **kwargs
        )[4]
        return shots

    def get_shots_per_touchtime(
        self,
        team_id: str = "current",
        last_n_games: int = 0,
        season: str = CURRENT_SEASON,
        opponent_team_id: str = 0,
        **kwargs,
    ):
        shots = self._get_shots(
            team_id, last_n_games, season, opponent_team_id, **kwargs
        )[6]
        return shots

    def __repr__(self):
        return f"<{self.__class__.__name__}_id={self.player_id}_name={self.name}>"


class NBAGame:
    """
    A class the represents an NBA game.
    """

    def __init__(self, game_id):
        self._game_id = game_id

    @property
    def game_id(self):
        return self._game_id

    @property
    def traiditional_stats(self, **kwargs):
        stats = BoxScoreTraditionalV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    @property
    def fourfactors_stats(self, **kwargs):
        stats = BoxScoreFourFactorsV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    @property
    def advanced_stats(self, **kwargs):
        stats = BoxScoreAdvancedV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    @property
    def usage_stats(self, **kwargs):
        stats = BoxScoreUsageV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    @property
    def playertrack_stats(self, **kwargs):
        stats = BoxScorePlayerTrackV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    @property
    def scoring_stats(self, **kwargs):
        stats = BoxScoreScoringV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    @property
    def matchup_stats(self, **kwargs):
        stats = BoxScoreMatchups(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    @property
    def defensive_stats(self, **kwargs):
        stats = BoxScoreDefensive(self.game_id, **kwargs).get_data_frames()[0]
        return stats

    @property
    def misc_stats(self, **kwargs):
        stats = BoxScoreMiscV2(self.game_id, **kwargs).get_data_frames()[0]
        return stats
