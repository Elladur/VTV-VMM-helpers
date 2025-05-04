"""
script to update a synced database which contain the matches in an event table
"""

import os
from datetime import datetime

from sqlalchemy import Connection, create_engine, text

from vtv_api_client import VtvApiClient


class DatabaseUpdater(VtvApiClient):
    """class representing crawler"""

    def __init__(
        self,
        club_id: int,
        start_date: datetime,
        end_date: datetime,
        api_key: str,
        database_uri: str,
    ):
        super().__init__(club_id, start_date, end_date, api_key)
        self.db_engine = create_engine(database_uri)

    def save_games(self, dryrun: bool = False) -> None:
        """print all games in a format that can be pasted into calendar"""
        home_games = self.games[
            self.games[self.home_column].str.contains(self.club_name)
        ]

        with self.db_engine.connect() as conn:
            if not dryrun:
                self.prepare_temp_table(conn)

            for day in sorted(home_games[self.day_column].drop_duplicates()):
                games_of_day = home_games[(home_games[self.day_column] == day)]
                event_text = "<p><strong>Heimspiele:</strong><br>"

                for _, game in games_of_day.iterrows():
                    event_text += self.get_game_as_text(game, False) + "<br>"

                event_text += "</p>"
                print(event_text)
                if not dryrun:
                    self.add_to_temp_table(conn, event_text, day)

            if not dryrun:
                self.merge_events(conn)
                conn.execute(text("drop temporary table tevent"))
                conn.commit()

    def merge_events(self, conn: Connection):
        delete_command = text(
            "delete e from event e where e.title = 'VMM' and e.date >= current_timestamp() and not exists(select * from tevent te where te.title = e.title and te.date = e.date);"
        )

        update_command = text(
            "update event e join tevent te on te.title = e.title and te.date = e.date set e.text = te.text, e.updated_at = current_timestamp() where te.date >= current_timestamp();"
        )

        insert_command = text(
            "insert event(title, text, `date`, created_at, updated_at, created_by, updated_by)"
            + "select te.title, te.text, te.date, te.created_at, te.updated_at, te.created_by, te.updated_by from tevent te "
            + "where te.date >= current_timestamp()"
            + "and not exists(select * from event e where te.title = e.title and te.date = e.date);"
        )
        conn.execute(delete_command)
        conn.execute(update_command)
        conn.execute(insert_command)

    def prepare_temp_table(self, conn: Connection):
        sql = text(
            "create temporary table tevent (title varchar(20) collate utf8mb4_unicode_ci, text varchar(500) collate utf8mb4_unicode_ci, date datetime, created_at datetime, updated_at datetime, created_by varchar(50) collate utf8mb4_unicode_ci, updated_by varchar(50) collate utf8mb4_unicode_ci);"
        )
        return conn.execute(sql)

    def add_to_temp_table(self, conn, content: str, day: datetime):
        sql = text(
            "insert tevent(title, text, date, created_at, updated_at, created_by, updated_by) values ('VMM', :text, :date, current_timestamp(), current_timestamp(), 'vtv_sync', 'vtv_sync')"
        )
        return conn.execute(sql, {"text": content, "date": day})


if __name__ == "__main__":
    # params
    CLUB_ID = int(os.getenv("CLUB_ID"))  # type: ignore
    START_DATE = datetime.today()
    END_DATE = datetime.fromisoformat(os.getenv("END_DATE"))  # type: ignore
    API_KEY = os.getenv("API_KEY")  # type: ignore
    DATABASE_URI = os.getenv("DATABASE_URI")  # type: ignore

    db_updater = DatabaseUpdater(
        CLUB_ID,
        START_DATE,
        END_DATE,
        API_KEY,  # type: ignore
        DATABASE_URI,  # type: ignore
    )
    db_updater.get_games()
    db_updater.save_games(dryrun=True)
