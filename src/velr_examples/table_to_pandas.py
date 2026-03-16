from __future__ import annotations

"""Convert an existing Velr result table to pandas.

This example shows how to run a query with `exec_one()`, work with the
returned result table, and convert that table directly to a pandas
DataFrame.

In this small graph we store:

- people
- movies

and connect them with relationships such as:

- (:Person)-[:ACTED_IN]->(:Movie)

This lets us stream or inspect query results first, and only then
materialize the same table as a pandas DataFrame when needed.
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
        # - Leonardo DiCaprio acted in Inception
        db.run(
            r"""
            CREATE
              (keanu:Person:Actor {name:'Keanu Reeves'}),
              (carrie:Person:Actor {name:'Carrie-Anne Moss'}),
              (laurence:Person:Actor {name:'Laurence Fishburne'}),
              (leo:Person:Actor {name:'Leonardo DiCaprio'}),

              (matrix:Movie {title:'The Matrix', released:1999}),
              (inception:Movie {title:'Inception', released:2010}),

              (keanu)-[:ACTED_IN {role:'Neo'}]->(matrix),
              (carrie)-[:ACTED_IN {role:'Trinity'}]->(matrix),
              (laurence)-[:ACTED_IN {role:'Morpheus'}]->(matrix),
              (leo)-[:ACTED_IN {role:'Cobb'}]->(inception);
            """
        )

        # Run a query and obtain a single result table.
        #
        # Read:
        #   (p:Person)-[:ACTED_IN]->(m:Movie)
        #
        # as:
        #   "find a person `p` and the movie `m` they acted in."
        with db.exec_one(
            r"""
            MATCH (p:Person)-[r:ACTED_IN]->(m:Movie)
            RETURN
              p.name AS actor,
              m.title AS movie,
              m.released AS released,
              r.role AS role
            ORDER BY released, movie, actor
            """
        ) as table:
            print("result table column names:")
            print(table.column_names())

            # Convert the existing result table directly to pandas.
            df = table.to_pandas()

            print()
            print("result table converted to pandas:")
            print(df)

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