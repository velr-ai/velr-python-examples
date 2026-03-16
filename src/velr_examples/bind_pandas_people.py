from __future__ import annotations

"""Bind a pandas DataFrame into Velr with the Velr Python driver.

This example shows how to take tabular data from pandas, bind it into
Velr under a logical name, and create graph nodes from it.

In this small dataset we store:

- people
- ages
- teams

We then bind the pandas DataFrame as an external table and use:

- UNWIND BIND('_people') AS r

to turn each dataframe row into graph data.

This lets us load normal dataframe data into a graph and then query it
back out with Cypher.
"""

import pandas as pd
from velr.driver import Velr


def main() -> None:
    # Create a small pandas DataFrame.
    #
    # In this example:
    # - Frodo and Sam are in Engineering
    # - Merry is in Operations
    # - each row becomes a Person node in the graph
    df = pd.DataFrame(
        [
            {"name": "Frodo Baggins", "age": 50, "team": "Engineering"},
            {"name": "Samwise Gamgee", "age": 38, "team": "Engineering"},
            {"name": "Meriadoc Brandybuck", "age": 36, "team": "Operations"},
        ]
    )

    with Velr.open(None) as db:
        # Bind the pandas DataFrame into Velr under the logical name
        # "_people".
        db.bind_pandas("_people", df)

        # Load the bound rows into the graph.
        #
        # Read:
        #   UNWIND BIND('_people') AS r
        #
        # as:
        #   "iterate over each bound row `r` from the external table
        #    named '_people'."
        db.run(
            r"""
            UNWIND BIND('_people') AS r
            CREATE (:Person {
              name: r.name,
              age: r.age,
              team: r.team
            })
            """
        )

        # Query the graph to show the imported people.
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN
              p.name AS name,
              p.age AS age,
              p.team AS team
            ORDER BY team, name
            """
        ) as table:
            print("people loaded from pandas into the graph:")

            with table.rows() as rows:
                for row in rows:
                    name, age, team = row
                    print(
                        f"  {name.as_python()} "
                        f"(age {age.as_python()}) -> {team.as_python()}"
                    )

        # Export the graph data back to pandas.
        out = db.to_pandas(
            r"""
            MATCH (p:Person)
            RETURN
              p.name AS name,
              p.age AS age,
              p.team AS team
            ORDER BY team, name
            """
        )

        print()
        print("graph data exported back to pandas:")
        print(out)


if __name__ == "__main__":
    main()