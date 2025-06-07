"""
script to generate weekly blocks of text that contains the VMM matches of the week
"""

import pyperclip as pc

from vtv_vmm_helpers.vtv_api_client import VtvApiClient


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
