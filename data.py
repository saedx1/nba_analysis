"""
This module holds the nba data fetching functions.
It either fetches them from the nba_api or the local storage.
"""
import os
from pathlib import Path
import pandas as pd
from nba_api.stats.static import teams, players
from nba_api.stats.endpoints import TeamGameLog

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
    if not nba_teams:
        nba_teams = teams.get_teams()
        nba_teams = {i["abbreviation"]: i for i in nba_teams}
        nba_teams = pd.DataFrame(nba_teams).T
        save_dataframe(nba_teams, "nba_teams.parquet")

    return nba_teams


def get_players() -> pd.DataFrame:
    """
    Get nba players in a dataframe.
    """
    filename = "nba_players.parquet"
    nba_players = get_dataframe(filename)
    if not nba_players:
        nba_players = players.get_players()
        nba_players = {i["full_name"]: i for i in nba_players}
        nba_players = pd.DataFrame(nba_players).T
        save_dataframe(nba_players, filename)

    return nba_players


def get_season(team_id: str, season: str, invalidate: bool = False) -> pd.DataFrame:
    """
    Get nba season for an nba team.
    """
    filename = f"{team_id}_{season}.parquet"
    if not invalidate:
        team_season = get_dataframe(filename)
    else:
        invalidate = True

    if invalidate:
        team_season = TeamGameLog(team_id, season).get_data_frames()[0]
        save_dataframe(team_season, filename)

    return team_season
