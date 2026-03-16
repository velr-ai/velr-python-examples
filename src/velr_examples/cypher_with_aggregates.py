from __future__ import annotations

"""WITH + aggregate example for the Velr Python driver.

This example shows how to use `WITH` together with aggregate functions
in openCypher.

Query shape:
  MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
  WITH m.title AS movie, count(p) AS actors
  WHERE actors >= 2
  RETURN movie, actors

Meaning:
  first group rows by movie and count how many actors each movie has,
  then pass the grouped result forward with `WITH`,
  then filter the grouped rows with `WHERE`.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small movie graph.
        db.run(
            r"""
            CREATE
              (keanu:Person {name:'Keanu Reeves'}),
              (carrie:Person {name:'Carrie-Anne Moss'}),
              (laurence:Person {name:'Laurence Fishburne'}),
              (hugo:Person {name:'Hugo Weaving'}),
              (matrix:Movie {title:'The Matrix'}),
              (john_wick:Movie {title:'John Wick'}),
              (keanu)-[:ACTED_IN]->(matrix),
              (carrie)-[:ACTED_IN]->(matrix),
              (laurence)-[:ACTED_IN]->(matrix),
              (hugo)-[:ACTED_IN]->(matrix),
              (keanu)-[:ACTED_IN]->(john_wick);
            """
        )

        # `MATCH` produces one row per (person, movie) pair.
        #
        # `WITH m.title AS movie, count(p) AS actors`
        # groups those rows by movie title and counts how many actors each movie has.
        #
        # After that, `WHERE actors >= 2`
        # filters the grouped rows, not the original match rows.
        with db.exec_one(
            r"""
            MATCH (p:Person)-[:ACTED_IN]->(m:Movie)
            WITH m.title AS movie, count(p) AS actors
            WHERE actors >= 2
            RETURN movie, actors
            ORDER BY actors DESC, movie
            """
        ) as table:
            print("movies with at least two actors:")

            with table.rows() as rows:
                for row in rows:
                    movie, actors = row
                    print(f"  {movie.as_python()} ({actors.as_python()} actors)")


if __name__ == "__main__":
    main()