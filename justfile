set shell := ["powershell", "-c"]
list:
    @just --list 

update:
    uv run ./src/main.py --no-dry-run

dry-run:
    uv run ./src/main.py --dry-run