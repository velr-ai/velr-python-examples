from __future__ import annotations

"""UNWIND example for the Velr Python driver.

This example shows how to use `UNWIND` in openCypher.

Query shape:
  UNWIND ['Frodo', 'Sam', 'Gandalf'] AS name
  RETURN name

Meaning:
  take a list value, turn each element into its own row,
  and then continue the query with one row per element.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # `UNWIND` turns each element in a list into a separate row.
        #
        # Here:
        # - the list is ['Frodo', 'Sam', 'Gandalf']
        # - each element is bound to the variable `name`
        # - one Person node is created per row
        db.run(
            r"""
            UNWIND ['Frodo', 'Sam', 'Gandalf'] AS name
            CREATE (:Person {name: name})
            """
        )

        # Query the created nodes back to verify the result.
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN p.name AS name
            ORDER BY name
            """
        ) as table:
            print("people created with UNWIND:")

            with table.rows() as rows:
                for row in rows:
                    (name,) = row
                    print(f"  {name.as_python()}")


if __name__ == "__main__":
    main()