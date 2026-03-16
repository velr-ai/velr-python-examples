from __future__ import annotations

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Start a transaction, write some data, and then let the transaction
        # go out of scope without calling commit().
        with db.begin_tx() as tx:
            tx.run(
                r"""
                CREATE
                  (:Person {name:'Frodo Baggins'}),
                  (:Person {name:'Samwise Gamgee'});
                """
            )

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

            print("dropping transaction without commit...")

        # Because the transaction was not committed, the database is unchanged.
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN count(p) AS people
            """
        ) as table:
            with table.rows() as rows:
                for row in rows:
                    (people,) = row
                    print(f"rows visible after transaction drop: {people.as_python()}")


if __name__ == "__main__":
    main()