from __future__ import annotations

from pathlib import Path

from velr.driver import Velr


def main() -> None:
    # Open an in-memory database.
    with Velr.open(None) as db:
        db.run("CREATE (:Example {name:'in-memory'})")
        print("opened in-memory database")

    # Open a file-backed database.
    path = Path("basic_open.db")
    with Velr.open(str(path)) as db:
        db.run("CREATE (:Example {name:'file-backed'})")
        print(f"opened file-backed database at {path}")


if __name__ == "__main__":
    main()