from datetime import datetime
import os
import argparse
from vtv_vmm_helpers.database_updater import DatabaseUpdater
from vtv_vmm_helpers.weekly_schedule import ScheduleExtractor


def main():
    parser = argparse.ArgumentParser(description="VTV VMM Helpers")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subparser for extract_schedule
    subparsers.add_parser("extract_schedule", help="Extract schedule using environment variables")

    # Subparser for update_database
    update_parser = subparsers.add_parser(
        "update_database", help="Update database using environment variables"
    )
    update_parser.add_argument(
        "--dry-run",
        dest="is_dry_run",
        action="store_true",
        help="Run in dry-run mode (no database changes)",
    )
    update_parser.set_defaults(is_dry_run=False)

    args = parser.parse_args()

    if args.command == "extract_schedule":
        extract_schedule()
    elif args.command == "update_database":
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
