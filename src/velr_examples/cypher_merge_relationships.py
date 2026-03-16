from __future__ import annotations

"""MERGE example for the Velr Python driver.

This example shows how to use `MERGE` for both nodes and relationships.

Query shape:
  MERGE (a:Person {name:'Frodo'})
  MERGE (b:Person {name:'Sam'})
  MERGE (a)-[:KNOWS]->(b)

Meaning:
  find the matching nodes and relationship, or create them if they do not exist.

This is useful for idempotent graph writes:
running the same query multiple times should not create duplicate nodes
or duplicate relationships.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Run the same MERGE pattern multiple times.
        #
        # The graph should still end up with:
        # - one Frodo node
        # - one Sam node
        # - one KNOWS relationship from Frodo to Sam
        db.run(
            r"""
            MERGE (a:Person {name:'Frodo Baggins'})
            MERGE (b:Person {name:'Samwise Gamgee'})
            MERGE (a)-[:KNOWS]->(b);

            MERGE (a:Person {name:'Frodo Baggins'})
            MERGE (b:Person {name:'Samwise Gamgee'})
            MERGE (a)-[:KNOWS]->(b);

            MERGE (a:Person {name:'Frodo Baggins'})
            MERGE (b:Person {name:'Samwise Gamgee'})
            MERGE (a)-[:KNOWS]->(b);
            """
        )

        # Add another relationship to show the graph can still grow normally.
        db.run(
            r"""
            MERGE (a:Person {name:'Frodo Baggins'})
            MERGE (b:Person {name:'Gandalf'})
            MERGE (a)-[:KNOWS]->(b);
            """
        )

        # Query the relationships back.
        with db.exec_one(
            r"""
            MATCH (a:Person)-[:KNOWS]->(b:Person)
            RETURN a.name AS from, b.name AS to
            ORDER BY from, to
            """
        ) as table:
            print("relationships after MERGE:")

            with table.rows() as rows:
                for row in rows:
                    from_, to = row
                    print(f"  {from_.as_python()} -> {to.as_python()}")

        # Show that the Frodo -> Sam relationship exists only once.
        with db.exec_one(
            r"""
            MATCH (:Person {name:'Frodo Baggins'})-[r:KNOWS]->(:Person {name:'Samwise Gamgee'})
            RETURN count(r) AS count
            """
        ) as table:
            with table.rows() as rows:
                for row in rows:
                    (count,) = row
                    print()
                    print(f"Frodo -> Sam relationship count: {count.as_python()}")


if __name__ == "__main__":
    main()