import typing
from datetime import datetime

import pandas as pd
import requests as re


class VtvApiClient:
    """class representing crawler"""

    date_column = "scheduled"
    liga_column = "groupName"
    home_column = "home"
    guest_column = "guest"
    day_column = "day"
    week_column = "week"
    home_won_matches_column = "matchesHome"
    guest_won_matches_column = "matchesGuest"

    def __init__(
        self,
        club_id: int,
        start_date: datetime,
        end_date: datetime,
        api_key: str,
    ):
        if start_date >= end_date:
            raise ValueError("start date must before end date")
        self.games: pd.DataFrame
        self.club_id = club_id
        self.start_date = start_date
        self.end_date = end_date
        self.api_key = api_key
        self.club_name: str

    def sort_games(self):
        """sort parsed games due to date"""
        self.games = self.games.sort_values(self.date_column)

    def get_game_as_text(self, game: dict, including_matches: bool) -> str:
        """print one game in a line"""
        game_str = f"{game[self.date_column].strftime('%d.%m.%Y %H:%M')}: {game[self.liga_column]} - {game[self.home_column]} gegen {game[self.guest_column]}"
        if including_matches:
            game_str += f" - {game[self.home_won_matches_column]}:{game[self.guest_won_matches_column]}"
        return game_str

    def query_api(self) -> typing.Any:
        """
        get the content of the vtv webpage
        depending on the date you get 1 or 2 pages, because past and future is seperated
        """
        header = {"Referer": "https://www.vorarlbergtennis.at/vereine/VTV/30015"}
        url = "https://www.vorarlbergtennis.at/"
        club_params = {
            "oetvappapi": "1",
            "apikey": self.api_key,
            "method": "nu-club",
            "clubId": self.club_id,
            "fed": "VTV",
        }

        club_result = re.get(url, headers=header, params=club_params, timeout=30)  # type: ignore
        self.club_name = club_result.json()["data"]["club"]["name"]

        params = {
            "oetvappapi": "1",
            "apikey": self.api_key,
            "method": "nu-club-meetings",
            "clubId": self.club_id,
            "startDate": self.start_date.strftime("%Y-%m-%d"),
            "endDate": self.end_date.strftime("%Y-%m-%d"),
            "fed": "VTV",
        }

        result = re.get(url, params, timeout=30, headers=header)  # type: ignore
        return result.json()

    def parse_json_result(self, json_result: dict) -> None:
        """get the games from the webpage"""
        self.games = pd.json_normalize(json_result["data"]["meetings"])

        self.games[self.date_column] = (
            pd.to_datetime(self.games[self.date_column])
            .dt.tz_convert("Europe/Vienna")
            .dt.tz_localize(None)
        )
        self.games[self.day_column] = self.games[self.date_column].dt.date
        self.games[self.week_column] = self.games[self.date_column].dt.isocalendar()[
            self.week_column
        ]

    def get_games(self) -> None:
        """
        this is the public interface. this executes all method in the right way
        to get the expected output of the class input parameter
        """
        json_result = self.query_api()

        if json_result["success"] is True:
            self.parse_json_result(json_result)
            self.sort_games()
        else:
            print("api call returned no success result")
