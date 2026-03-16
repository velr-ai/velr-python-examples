from __future__ import annotations

"""Round-trip org chart data through pandas with the Velr Python driver.

This example shows how to start with tabular org chart data in pandas,
load it into Velr, model it as a graph, and export graph-derived
results back to pandas.

In this small dataset we store:

- people
- teams
- managers

We then bind the pandas DataFrame as an external table and use it to
create:

- (:Person) nodes
- (:Team) nodes
- (:Person)-[:MEMBER_OF]->(:Team) relationships
- (:Person)-[:REPORTS_TO]->(:Person) relationships

This lets us move between dataframe-shaped data and graph-shaped data
in a natural way.
"""

import pandas as pd
from velr.driver import Velr


def main() -> None:
    # Create a small pandas DataFrame representing an org chart.
    #
    # In this example:
    # - Frodo and Sam are in Engineering and report to Aragorn
    # - Merry is in Operations and reports to Gandalf
    # - Aragorn and Gandalf report to Elrond
    df = pd.DataFrame(
        [
            {
                "name": "Frodo Baggins",
                "title": "Engineer",
                "team": "Engineering",
                "manager": "Aragorn",
            },
            {
                "name": "Samwise Gamgee",
                "title": "Engineer",
                "team": "Engineering",
                "manager": "Aragorn",
            },
            {
                "name": "Meriadoc Brandybuck",
                "title": "Operations Specialist",
                "team": "Operations",
                "manager": "Gandalf",
            },
            {
                "name": "Aragorn",
                "title": "Engineering Manager",
                "team": "Engineering",
                "manager": "Elrond",
            },
            {
                "name": "Gandalf",
                "title": "Operations Manager",
                "team": "Operations",
                "manager": "Elrond",
            },
            {
                "name": "Elrond",
                "title": "Director",
                "team": "Leadership",
                "manager": None,
            },
        ]
    )

    with Velr.open(None) as db:
        # Bind the pandas DataFrame into Velr under the logical name
        # "_org".
        db.bind_pandas("_org", df)

        # Create Person nodes from the bound rows.
        #
        # Read:
        #   UNWIND BIND('_org') AS r
        #
        # as:
        #   "iterate over each bound row `r` from the external table
        #    named '_org'."
        db.run(
            r"""
            UNWIND BIND('_org') AS r
            CREATE (:Person {
              name: r.name,
              title: r.title
            })
            """
        )

        # Create Team nodes from the same bound rows.
        db.run(
            r"""
            UNWIND BIND('_org') AS r
            MERGE (:Team {name: r.team})
            """
        )

        # Connect each person to their team.
        db.run(
            r"""
            UNWIND BIND('_org') AS r
            MATCH (p:Person {name: r.name})
            MATCH (t:Team {name: r.team})
            MERGE (p)-[:MEMBER_OF]->(t)
            """
        )

        # Connect each person to their manager.
        #
        # Rows where manager is NULL do not create a reporting edge.
        db.run(
            r"""
            UNWIND BIND('_org') AS r
            MATCH (employee:Person {name: r.name})
            MATCH (manager:Person {name: r.manager})
            MERGE (employee)-[:REPORTS_TO]->(manager)
            """
        )

        # Query the graph to show people, their teams, and their direct
        # managers.
        with db.exec_one(
            r"""
            MATCH (p:Person)-[:MEMBER_OF]->(t:Team)
            OPTIONAL MATCH (p)-[:REPORTS_TO]->(manager:Person)
            RETURN
              p.name AS person,
              p.title AS title,
              t.name AS team,
              manager.name AS manager
            ORDER BY team, person
            """
        ) as table:
            print("people, their teams, and their managers:")

            with table.rows() as rows:
                for row in rows:
                    person, title, team, manager = row
                    print(
                        f"  {person.as_python()} "
                        f"({title.as_python()}) -> "
                        f"{team.as_python()} "
                        f"[manager: {manager.as_python()}]"
                    )

        # Export graph-derived org chart data back to pandas.
        out = db.to_pandas(
            r"""
            MATCH (employee:Person)-[:MEMBER_OF]->(team:Team)
            OPTIONAL MATCH (employee)-[:REPORTS_TO]->(manager:Person)
            RETURN
              employee.name AS employee,
              employee.title AS title,
              team.name AS team,
              manager.name AS manager
            ORDER BY team, employee
            """
        )

        print()
        print("graph data exported back to pandas:")
        print(out)

        # Because the result is now a normal pandas DataFrame, we can
        # use regular dataframe operations on it.
        summary = (
            out.groupby("team", as_index=False)
            .size()
            .rename(columns={"size": "people_in_team"})
            .sort_values("team")
        )

        print()
        print("people per team:")
        print(summary)


if __name__ == "__main__":
    main()