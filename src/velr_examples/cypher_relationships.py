from __future__ import annotations

"""Basic relationship matching example for the Velr Python driver.

This example shows one of the core ideas in openCypher:
matching relationships between nodes.

Query pattern:
  (p:Person)-[:ACTED_IN]->(m:Movie)

Meaning:
  find Person nodes connected by an outgoing ACTED_IN relationship
  to Movie nodes.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small movie graph with:
        # - Person nodes
        # - Movie nodes
        # - ACTED_IN relationships from people to movies
        #
        # In openCypher:
        # - `(n:Label)` is a node with a label
        # - `-[:TYPE]->` is a directed relationship
        db.run(
            r"""
            CREATE
              (keanu:Person {name:'Keanu Reeves'}),
              (carrie:Person {name:'Carrie-Anne Moss'}),
              (laurence:Person {name:'Laurence Fishburne'}),
              (matrix:Movie {title:'The Matrix', released:1999}),
              (john_wick:Movie {title:'John Wick', released:2014}),
              (keanu)-[:ACTED_IN]->(matrix),
              (carrie)-[:ACTED_IN]->(matrix),
              (laurence)-[:ACTED_IN]->(matrix),
              (keanu)-[:ACTED_IN]->(john_wick);
            """
        )

        # Match the pattern:
        #
        #   (p:Person)-[:ACTED_IN]->(m:Movie)
        #
        # Read it as:
        # "find a Person node `p` that has an outgoing ACTED_IN relationship
        #  to a Movie node `m`."
        #
        # Then return the actor name and movie title for each match.
        with db.exec_one(
            r"""
            MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
            RETURN p.name AS actor, m.title AS movie
            ORDER BY actor, movie
            """
        ) as table:
            print("actors and their movies:")

            with table.rows() as rows:
                for row in rows:
                    actor, movie = row
                    print(f"  {actor.as_python()} -> {movie.as_python()}")


if __name__ == "__main__":
    main()