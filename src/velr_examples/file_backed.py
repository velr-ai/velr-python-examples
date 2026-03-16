from __future__ import annotations

from pathlib import Path

from velr.driver import Velr

DB_PATH = Path("file_backed_example.velr")


def main() -> None:
    # Start from a clean file so the example is repeatable.
    DB_PATH.unlink(missing_ok=True)

    # Open a file-backed database and write some data.
    with Velr.open(str(DB_PATH)) as db:
        db.run(
            r"""
            CREATE
              (:Person {name:'Frodo Baggins', role:'Ring-bearer'}),
              (:Person {name:'Samwise Gamgee', role:'Companion'}),
              (:Person {name:'Gandalf', role:'Wizard'});
            """
        )
        print(f"wrote data to {DB_PATH}")

    # Reopen the same database file and verify that the data is still there.
    with Velr.open(str(DB_PATH)) as db:
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN p.name AS name, p.role AS role
            ORDER BY name
            """
        ) as table:
            print(f"reopened {DB_PATH}")
            print("persisted rows:")

            with table.rows() as rows:
                for row in rows:
                    name, role = row
                    print(f"  {name.as_python()} ({role.as_python()})")


if __name__ == "__main__":
    main()