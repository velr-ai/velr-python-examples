from __future__ import annotations

"""WHERE filtering example for the Velr Python driver.

This example shows how to filter query results with `WHERE`.

Query shape:
  MATCH (p:Person)
  WHERE p.born < 1965
  RETURN p.name, p.born

Meaning:
  find Person nodes, keep only the ones that match the condition,
  and return values from the remaining rows.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a few Person nodes to query.
        db.run(
            r"""
            CREATE
              (:Person {name:'Keanu Reeves', born:1964}),
              (:Person {name:'Carrie-Anne Moss', born:1967}),
              (:Person {name:'Laurence Fishburne', born:1961}),
              (:Person {name:'Hugo Weaving', born:1960});
            """
        )

        # `MATCH` finds candidate rows.
        # `WHERE` filters those rows.
        #
        # Read:
        #   MATCH (p:Person)
        #   WHERE p.born < 1965
        #
        # as:
        #   "find Person nodes, then keep only the ones born before 1965."
        with db.exec_one(
            r"""
            MATCH (p:Person)
            WHERE p.born < 1965
            RETURN p.name AS name, p.born AS born
            ORDER BY born, name
            """
        ) as table:
            print("people born before 1965:")

            with table.rows() as rows:
                for row in rows:
                    name, born = row
                    print(f"  {name.as_python()} ({born.as_python()})")


if __name__ == "__main__":
    main()