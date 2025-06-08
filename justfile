set shell := ["powershell", "-c"]

# lists all the available recipes
list:
    @just --list 

# Updates Tennisclub homepages with current VMM matches
update:
    uv run ./src/main.py update_database

# tests if connection to vtv homepage and database is possible and answers can be parsed
testupdate:
    uv run ./src/main.py update_database --dry-run

# gets current results of season and schedule of remaining matches
extract:
    uv run ./src/main.py extract_schedule