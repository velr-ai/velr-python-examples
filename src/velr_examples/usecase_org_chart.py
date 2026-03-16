from __future__ import annotations

"""Organization chart example for the Velr Python driver.

This example shows how a graph can model an organization chart.

In this small graph we store:

- people
- teams

and connect them with relationships such as:

- (:Person)-[:REPORTS_TO]->(:Person)
- (:Person)-[:MEMBER_OF]->(:Team)
- (:Person)-[:MANAGES]->(:Team)

This lets us ask questions such as:
"Who reports to whom, which team is a person part of,
and who manages that team?"
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small org chart.
        #
        # In this example:
        # - Frodo and Sam are in Engineering
        # - Merry is in Operations
        # - Aragorn manages Engineering
        # - Gandalf manages Operations
        # - Frodo and Sam report to Aragorn
        # - Merry reports to Gandalf
        # - Aragorn and Gandalf report to Elrond
        db.run(
            r"""
            CREATE
              (frodo:Person {name:'Frodo Baggins', title:'Engineer'}),
              (sam:Person {name:'Samwise Gamgee', title:'Engineer'}),
              (merry:Person {name:'Meriadoc Brandybuck', title:'Operations Specialist'}),
              (aragorn:Person {name:'Aragorn', title:'Engineering Manager'}),
              (gandalf:Person {name:'Gandalf', title:'Operations Manager'}),
              (elrond:Person {name:'Elrond', title:'Director'}),

              (engineering:Team {name:'Engineering'}),
              (operations:Team {name:'Operations'}),

              (frodo)-[:MEMBER_OF]->(engineering),
              (sam)-[:MEMBER_OF]->(engineering),
              (merry)-[:MEMBER_OF]->(operations),
              (aragorn)-[:MEMBER_OF]->(engineering),
              (gandalf)-[:MEMBER_OF]->(operations),

              (aragorn)-[:MANAGES]->(engineering),
              (gandalf)-[:MANAGES]->(operations),

              (frodo)-[:REPORTS_TO]->(aragorn),
              (sam)-[:REPORTS_TO]->(aragorn),
              (merry)-[:REPORTS_TO]->(gandalf),
              (aragorn)-[:REPORTS_TO]->(elrond),
              (gandalf)-[:REPORTS_TO]->(elrond);
            """
        )

        # Traverse the graph from a person, to their team, to the
        # person who manages that team:
        #
        #   (p:Person)-[:MEMBER_OF]->(t:Team)<-[:MANAGES]-(manager:Person)
        #
        # Read this as:
        # "find a person `p`, the team `t` they belong to, and the
        # manager `manager` of that team."
        with db.exec_one(
            r"""
            MATCH (p:Person)-[:MEMBER_OF]->(t:Team)<-[:MANAGES]-(manager:Person)
            RETURN
              p.name AS person,
              t.name AS team,
              manager.name AS manager
            ORDER BY team, person
            """
        ) as table:
            print("people, their team, and team manager:")

            with table.rows() as rows:
                for row in rows:
                    person, team, manager = row
                    print(
                        f"  {person.as_python()} -> {team.as_python()} "
                        f"(managed by {manager.as_python()})"
                    )

        # A graph is also useful for showing direct reporting lines.
        with db.exec_one(
            r"""
            MATCH (employee:Person)-[:REPORTS_TO]->(manager:Person)
            RETURN
              employee.name AS employee,
              manager.name AS manager
            ORDER BY manager, employee
            """
        ) as table:
            print()
            print("direct reporting lines:")

            with table.rows() as rows:
                for row in rows:
                    employee, manager = row
                    print(
                        f"  {employee.as_python()} reports to "
                        f"{manager.as_python()}"
                    )

        # Follow the management chain above Frodo.
        #
        # Read:
        #   (start:Person)-[:REPORTS_TO*1..3]->(manager:Person)
        #
        # as:
        #   "starting from Frodo, follow between 1 and 3 REPORTS_TO
        #    relationships upward through the org chart."
        with db.exec_one(
            r"""
            MATCH p = (start:Person {name:'Frodo Baggins'})-[:REPORTS_TO*1..3]->(manager:Person)
            RETURN
              start.name AS employee,
              manager.name AS manager,
              length(p) AS levels_up
            ORDER BY levels_up, manager
            """
        ) as table:
            print()
            print("management chain above Frodo:")

            with table.rows() as rows:
                for row in rows:
                    employee, manager, levels_up = row
                    print(
                        f"  {employee.as_python()} -> {manager.as_python()} "
                        f"({levels_up.as_python()} level(s) up)"
                    )


if __name__ == "__main__":
    main()