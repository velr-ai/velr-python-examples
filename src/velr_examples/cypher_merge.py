from __future__ import annotations

"""MERGE example for the Velr Python driver.

This example shows how to use `MERGE` in openCypher.

Query shape:
  MERGE (p:Person {name:'Frodo'})

Meaning:
  find a node that matches the given pattern, or create it if it does not exist.

`MERGE` is useful when you want idempotent writes:
running the same query multiple times should not create duplicates.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Run the same MERGE multiple times.
        #
        # Because the pattern is the same each time, this should leave us with
        # only one matching Person node.
        db.run(
            r"""
            MERGE (:Person {name:'Frodo Baggins'});
            MERGE (:Person {name:'Frodo Baggins'});
            MERGE (:Person {name:'Frodo Baggins'});
            """
        )

        # Add one more distinct person.
        db.run(
            r"""
            MERGE (:Person {name:'Samwise Gamgee'});
            """
        )

        # Query the graph back.
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN p.name AS name
            ORDER BY name
            """
        ) as table:
            print("people after MERGE:")

            with table.rows() as rows:
                for row in rows:
                    (name,) = row
                    print(f"  {name.as_python()}")

        # Show that Frodo exists only once.
        with db.exec_one(
            r"""
            MATCH (p:Person {name:'Frodo Baggins'})
            RETURN count(p) AS count
            """
        ) as table:
            with table.rows() as rows:
                for row in rows:
                    (count,) = row
                    print()
                    print(f"Frodo Baggins node count: {count.as_python()}")


if __name__ == "__main__":
    main()