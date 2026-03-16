from __future__ import annotations

from velr.driver import Velr


def main() -> None:
    # Open an in-memory database.
    with Velr.open(None) as db:
        # Start a transaction.
        with db.begin_tx() as tx:
            # All writes below are part of the same transaction and are not
            # permanently visible until we commit.
            tx.run(
                r"""
                CREATE
                  (:Person {name:'Keanu Reeves', born:1964}),
                  (:Person {name:'Carrie-Anne Moss', born:1967}),
                  (:Person {name:'Laurence Fishburne', born:1961});
                """
            )

            # Queries can also be executed inside the transaction.
            with tx.exec_one(
                r"""
                MATCH (p:Person)
                RETURN count(p) AS people
                """
            ) as table:
                with table.rows() as rows:
                    for row in rows:
                        (people,) = row
                        print(f"rows visible inside transaction: {people.as_python()}")

            # Commit makes the transaction durable.
            tx.commit()

        # After commit, the data is visible from the connection as usual.
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN p.name AS name
            ORDER BY name
            """
        ) as table:
            print("people after commit:")

            with table.rows() as rows:
                for row in rows:
                    (name,) = row
                    print(f"  {name.as_python()}")


if __name__ == "__main__":
    main()