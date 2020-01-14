from pathlib import Path
import click
import pandas as pd

import helpers
import data

LOGGER = helpers.get_logger()


class NBATeam:
    """
    A class that represents an NBA Team.
    """

    def __init__(self, name: str, team_id: str):
        self.name = name
        self.team_id = team_id

    def get_season(self, season: str, invalidate: bool = False) -> pd.DataFrame:
        """
        Gets team's matches for a whole season.
        """
        return data.get_season(self.team_id, season, invalidate)

    def get_last_matches(self, last_n_games: int) -> pd.DataFrame:
        """
        Get's last n games for a team in this season.
        """
        return self.get_season("2019-20", True).iloc[-last_n_games:]
