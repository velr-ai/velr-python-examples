from __future__ import annotations

"""Aggregate function example for the Velr Python driver.

This example shows how to use aggregate functions in openCypher.

Query shape:
  MATCH (p:Person)
  RETURN count(p), min(p.born), max(p.born), avg(p.born), collect(p.name)

Meaning:
  match many rows, then compute summary values across those rows.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a few Person nodes we can aggregate over.
        db.run(
            r"""
            CREATE
              (:Person {name:'Keanu Reeves', born:1964}),
              (:Person {name:'Carrie-Anne Moss', born:1967}),
              (:Person {name:'Laurence Fishburne', born:1961}),
              (:Person {name:'Hugo Weaving', born:1960});
            """
        )

        # Aggregate functions summarize the matched rows:
        #
        # - count(p)     -> number of matched rows
        # - min(...)     -> smallest value
        # - max(...)     -> largest value
        # - avg(...)     -> average value
        # - collect(...) -> list of values
        #
        # Because this query only returns aggregate expressions,
        # it produces a single result row.
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN
              count(p) AS people,
              min(p.born) AS first_born,
              max(p.born) AS last_born,
              avg(p.born) AS average_born,
              collect(p.name) AS names
            """
        ) as table:
            print("aggregate results:")

            with table.rows() as rows:
                for row in rows:
                    people, first_born, last_born, average_born, names = row

                    print(f"  people: {people.as_python()}")
                    print(f"  first born: {first_born.as_python()}")
                    print(f"  last born: {last_born.as_python()}")
                    print(f"  average born: {average_born.as_python()}")
                    print(f"  names: {names.as_python(parse_json=True)}")


if __name__ == "__main__":
    main()