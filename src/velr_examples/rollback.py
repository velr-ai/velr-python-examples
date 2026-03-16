from __future__ import annotations

from velr.driver import Velr


def main() -> None:
    # Open an in-memory database.
    with Velr.open(None) as db:
        # Start a transaction.
        with db.begin_tx() as tx:
            # These writes are only visible inside the transaction until it is committed.
            tx.run(
                r"""
                CREATE
                  (:Person {name:'Keanu Reeves', born:1964}),
                  (:Person {name:'Carrie-Anne Moss', born:1967});
                """
            )

            # Inside the transaction, the rows are visible.
            with tx.exec_one(
                r"""
                MATCH (p:Person)
                RETURN count(p) AS people
                """
            ) as table:
                with table.rows() as rows:
                    for row in rows:
                        (people,) = row
                        print(
                            "rows visible inside transaction before rollback: "
                            f"{people.as_python()}"
                        )

            # Roll back the transaction, discarding all writes done in it.
            tx.rollback()

        # After rollback, the database is unchanged.
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN count(p) AS people
            """
        ) as table:
            with table.rows() as rows:
                for row in rows:
                    (people,) = row
                    print(f"rows visible after rollback: {people.as_python()}")


if __name__ == "__main__":
    main()