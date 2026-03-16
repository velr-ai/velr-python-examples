from __future__ import annotations

"""Knowledge graph example for the Velr Python driver.

This example shows how a knowledge graph models entities and the
relationships between them.

In this small graph we store:

- people
- companies
- technologies

and connect them with relationships such as:

- (:Person)-[:WORKS_AT]->(:Company)
- (:Company)-[:USES]->(:Technology)
- (:Person)-[:KNOWS_ABOUT]->(:Technology)

This lets us ask connected questions such as:
"Which technologies is each person exposed to through their company?"
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small knowledge graph.
        #
        # The graph contains:
        # - people
        # - companies
        # - technologies
        # - relationships between them
        db.run(
            r"""
            CREATE
              (frodo:Person {name:'Frodo Baggins'}),
              (sam:Person {name:'Samwise Gamgee'}),
              (gandalf:Person {name:'Gandalf'}),
              (velr:Company {name:'Velr'}),
              (shire_it:Company {name:'Shire IT'}),
              (rust:Technology {name:'Rust'}),
              (sqlite:Technology {name:'SQLite'}),
              (graphs:Technology {name:'Graph Databases'}),
              (agents:Technology {name:'AI Agents'}),

              (frodo)-[:WORKS_AT]->(velr),
              (sam)-[:WORKS_AT]->(shire_it),
              (gandalf)-[:WORKS_AT]->(velr),

              (velr)-[:USES]->(rust),
              (velr)-[:USES]->(sqlite),
              (velr)-[:USES]->(graphs),
              (shire_it)-[:USES]->(sqlite),

              (frodo)-[:KNOWS_ABOUT]->(graphs),
              (sam)-[:KNOWS_ABOUT]->(sqlite),
              (gandalf)-[:KNOWS_ABOUT]->(rust),
              (gandalf)-[:KNOWS_ABOUT]->(agents);
            """
        )

        # Traverse the graph across multiple entity types:
        #
        #   (p:Person)-[:WORKS_AT]->(c:Company)-[:USES]->(t:Technology)
        #
        # Read this as:
        # "find a person `p`, the company `c` they work at, and the
        # technology `t` that company uses."
        with db.exec_one(
            r"""
            MATCH (p:Person)-[:WORKS_AT]->(c:Company)-[:USES]->(t:Technology)
            RETURN
              p.name AS person,
              c.name AS company,
              t.name AS technology
            ORDER BY person, technology
            """
        ) as table:
            print("technologies connected to people through their company:")

            with table.rows() as rows:
                for row in rows:
                    person, company, technology = row
                    print(
                        f"  {person.as_python()} -> {company.as_python()} -> "
                        f"{technology.as_python()}"
                    )

        # A knowledge graph is also useful for finding who knows about
        # a technology that a company uses.
        with db.exec_one(
            r"""
            MATCH (p:Person)-[:KNOWS_ABOUT]->(t:Technology)<-[:USES]-(c:Company)
            RETURN
              p.name AS person,
              t.name AS technology,
              c.name AS company
            ORDER BY company, technology, person
            """
        ) as table:
            print()
            print("people who know about technologies used by a company:")

            with table.rows() as rows:
                for row in rows:
                    person, technology, company = row
                    print(
                        f"  {person.as_python()} knows about "
                        f"{technology.as_python()} used by {company.as_python()}"
                    )


if __name__ == "__main__":
    main()