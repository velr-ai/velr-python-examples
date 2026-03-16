from __future__ import annotations

"""Basic MATCH example for the Velr Python driver.

This example shows the most basic openCypher query shape:
matching nodes and returning values from them.

Query pattern:
  MATCH (p:Person)
  RETURN p.name, p.born

Meaning:
  find all nodes with the label `Person` and return selected properties.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a few Person nodes we can query.
        #
        # In openCypher:
        # - `(n:Label)` creates a node with a label
        # - `{key:value}` sets properties on the node
        db.run(
            r"""
            CREATE
              (:Person {name:'Keanu Reeves', born:1964}),
              (:Person {name:'Carrie-Anne Moss', born:1967}),
              (:Person {name:'Laurence Fishburne', born:1961});
            """
        )

        # Match all Person nodes and return two properties from each one.
        #
        # Read:
        #   MATCH (p:Person)
        # as:
        #   "find every node `p` with the label Person"
        #
        # Then:
        #   RETURN p.name AS name, p.born AS born
        # selects which values to return for each match.
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN p.name AS name, p.born AS born
            ORDER BY born
            """
        ) as table:
            print("people:")

            with table.rows() as rows:
                for row in rows:
                    name, born = row
                    print(f"  {name.as_python()} ({born.as_python()})")


if __name__ == "__main__":
    main()