import streamlit as st
import pandas as pd
from inspect import getsource
from nba_api.stats.static import teams
from nba_api.stats.static import players
from nba_api.stats.endpoints import PlayerCareerStats


@st.cache
def get_teams():
    nba_teams = teams.get_teams()
    nba_teams = {i["abbreviation"]: i for i in nba_teams}
    return pd.DataFrame(nba_teams).T


@st.cache
def get_players():
    # get_players returns a list of dictionaries, each representing a player.
    nba_players = players.get_players()
    nba_players = {i["full_name"]: i for i in nba_players}
    nba_players = pd.DataFrame(nba_players).T
    nba_players.full_name = nba_players.full_name.str.lower()
    return nba_players[nba_players.is_active]


@st.cache
def get_player_stats(player_id):
    career = PlayerCareerStats(player_id=player_id)
    return career.get_data_frames()[0]


def main():
    st.title("MY NBA STATS")
    nba_teams = get_teams()
    nba_players = get_players()

    # option = st.multiselect(
    #     "Player Name",
    #     nba_players.id,
    #     format_func=lambda x: ,
    # )[0]
    # option = st.sidebar.selectbox(
    #     f"What player are you intersted in? ({len(nba_players)})", nba_players.id
    # )

    # st.sidebar.markdown("### What player are you intersted in?")

    option = st.sidebar.text_input("What player are you intersted in?")
    if option.lower() in nba_players.full_name.values:
        option = nba_players[nba_players.full_name == option.lower()]
        stats = get_player_stats(option.values[0][0])
        names = list(option.values[0][1])
        names[0] = names[0].upper()
        ln_idx = "".join(names).find(" ")
        names[ln_idx + 1] = names[ln_idx + 1].upper()
        st.write("".join(names))
        if st.checkbox("Show/Hide"):
            st.dataframe(stats)
    # "Team ID:", option
    # option = st.sidebar.selectbox(
    #     "What stats?", ["Points", "Assits", "Rebounds", "Blocks", "Steals"]
    # )


main()
