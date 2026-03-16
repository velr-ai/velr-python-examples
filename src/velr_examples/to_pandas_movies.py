from __future__ import annotations

"""Export query results to pandas with the Velr Python driver.

This example shows how to query graph data from Velr and materialize
the result as a pandas DataFrame.

In this small graph we store:

- people
- movies

and connect them with relationships such as:

- (:Person)-[:ACTED_IN]->(:Movie)
- (:Person)-[:DIRECTED]->(:Movie)

This lets us take graph-shaped data and work with it using standard
pandas dataframe operations.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small movie graph.
        #
        # In this example:
        # - Keanu Reeves acted in The Matrix
        # - Carrie-Anne Moss acted in The Matrix
        # - Laurence Fishburne acted in The Matrix
        # - Christopher Nolan directed Inception
        # - Leonardo DiCaprio acted in Inception
        db.run(
            r"""
            CREATE
              (keanu:Person:Actor {name:'Keanu Reeves'}),
              (carrie:Person:Actor {name:'Carrie-Anne Moss'}),
              (laurence:Person:Actor {name:'Laurence Fishburne'}),
              (leo:Person:Actor {name:'Leonardo DiCaprio'}),
              (nolan:Person:Director {name:'Christopher Nolan'}),

              (matrix:Movie {title:'The Matrix', released:1999}),
              (inception:Movie {title:'Inception', released:2010}),

              (keanu)-[:ACTED_IN {role:'Neo'}]->(matrix),
              (carrie)-[:ACTED_IN {role:'Trinity'}]->(matrix),
              (laurence)-[:ACTED_IN {role:'Morpheus'}]->(matrix),
              (leo)-[:ACTED_IN {role:'Cobb'}]->(inception),
              (nolan)-[:DIRECTED]->(inception);
            """
        )

        # Query the graph and export the result directly to pandas.
        #
        # Read:
        #   (p:Person)-[:ACTED_IN]->(m:Movie)
        #
        # as:
        #   "find a person `p` and the movie `m` they acted in."
        df = db.to_pandas(
            r"""
            MATCH (p:Person)-[r:ACTED_IN]->(m:Movie)
            RETURN
              p.name AS actor,
              m.title AS movie,
              m.released AS released,
              r.role AS role
            ORDER BY released, movie, actor
            """
        )

        print("actors and the movies they appeared in:")
        print(df)

        print()
        print("dataframe columns:")
        print(list(df.columns))

        # Because the result is now a normal pandas DataFrame, we can
        # use regular dataframe operations on it.
        summary = (
            df.groupby("movie", as_index=False)
            .size()
            .rename(columns={"size": "actor_count"})
            .sort_values("movie")
        )

        print()
        print("number of actors per movie:")
        print(summary)


if __name__ == "__main__":
    main()