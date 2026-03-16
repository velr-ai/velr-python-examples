from __future__ import annotations

"""Load CSV data with pandas and turn it into graph data with Velr.

This example shows how to read a CSV file with pandas, bind the
resulting DataFrame into Velr, and create graph nodes from it.

In this small dataset we store:

- people
- ages
- teams

We then bind the pandas DataFrame as an external table and use:

- UNWIND BIND('_people') AS r

to turn each CSV row into graph data.

This lets us move from CSV, to pandas, to graph queries in a natural
way.
"""

from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd
from velr.driver import Velr


def main() -> None:
    # Create a small CSV file.
    #
    # In this example:
    # - Frodo and Sam are in Engineering
    # - Merry is in Operations
    csv_text = """name,age,team
Frodo Baggins,50,Engineering
Samwise Gamgee,38,Engineering
Meriadoc Brandybuck,36,Operations
"""

    with TemporaryDirectory() as tmpdir:
        csv_path = Path(tmpdir) / "people.csv"
        csv_path.write_text(csv_text, encoding="utf-8")

        # Read the CSV file with pandas.
        df = pd.read_csv(csv_path)

        print("CSV loaded into pandas:")
        print(df)

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
                print()
                print("people loaded from CSV into the graph:")

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