""" 
script to generate weekly blocks of text that contains the VMM matches of the week
"""

import os
from datetime import datetime

import pyperclip as pc

from vtv_api_client import VtvApiClient


class ScheduleExtractor(VtvApiClient):
    """class representing crawler"""

    def print_games(self) -> None:
        """print all games in a format that can be pasted into calendar"""
        output = ""

        for w in sorted(self.games[self.week_column].drop_duplicates()):
            output += f"KW {w}\n"
            games_in_week = self.games[(self.games[self.week_column] == w)]
            output += "Heimspiele:\n"

            for _, game in games_in_week[
                games_in_week[self.home_column].str.contains(self.club_name)
            ].iterrows():
                output += self.get_game_as_text(game, True) + "\n"

            output += "Auswärtsspiele:\n"
            for _, game in games_in_week[
                games_in_week[self.guest_column].str.contains(self.club_name)
            ].iterrows():
                output += self.get_game_as_text(game, True) + "\n"
            output += "\n\n"
        pc.copy(output)
        print(output)


if __name__ == "__main__":
    # params
    CLUB_ID = int(os.getenv("CLUB_ID"))  # type: ignore
    START_DATE = datetime.fromisoformat(os.getenv("START_DATE"))  # type: ignore
    END_DATE = datetime.fromisoformat(os.getenv("END_DATE"))  # type: ignore
    API_KEY = os.getenv("API_KEY")  # type: ignore

    extractor = ScheduleExtractor(CLUB_ID, START_DATE, END_DATE, API_KEY)  # type: ignore
    extractor.get_games()
    extractor.print_games()
