from datetime import datetime
import os
import argparse
from vtv_vmm_helpers.database_updater import DatabaseUpdater
from vtv_vmm_helpers.weekly_schedule import ScheduleExtractor


def main():
    parser = argparse.ArgumentParser(description="VTV VMM Helpers")
    parser.add_argument(
        "--dry-run",
        dest="is_dry_run",
        action="store_true",
        help="Run in dry-run mode (no database changes)",
    )
    parser.add_argument(
        "--no-dry-run",
        dest="is_dry_run",
        action="store_false",
        help="Run and apply changes to the database (is the default behavior)",
    )
    parser.set_defaults(is_dry_run=False)
    args = parser.parse_args()

    update_database(is_dry_run=args.is_dry_run)


def extract_schedule():
    # params
    CLUB_ID = int(os.getenv("CLUB_ID"))  # type: ignore
    START_DATE = datetime.fromisoformat(os.getenv("START_DATE"))  # type: ignore
    END_DATE = datetime.fromisoformat(os.getenv("END_DATE"))  # type: ignore
    API_KEY = os.getenv("API_KEY")  # type: ignore

    extractor = ScheduleExtractor(CLUB_ID, START_DATE, END_DATE, API_KEY)  # type: ignore
    extractor.get_games()
    extractor.print_games()


def update_database(is_dry_run: bool = True):
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
    db_updater.save_games(is_dry_run)


if __name__ == "__main__":
    main()
