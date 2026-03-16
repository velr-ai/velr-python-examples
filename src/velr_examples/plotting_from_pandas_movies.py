from __future__ import annotations

"""Plot graph-derived data with pandas and matplotlib.

This example shows how to query graph data from Velr, materialize the
result as a pandas DataFrame, and visualize it with matplotlib.

In this small graph we store:

- people
- movies

and connect them with relationships such as:

- (:Person)-[:ACTED_IN]->(:Movie)
- (:Person)-[:DIRECTED]->(:Movie)

This lets us use Velr for graph-shaped data and standard Python tools
for dataframe analysis and plotting.
"""

import matplotlib.pyplot as plt
from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small movie graph.
        #
        # In this example:
        # - The Matrix has 3 actors
        # - Inception has 2 actors
        # - Interstellar has 1 actor
        db.run(
            r"""
            CREATE
              (keanu:Person:Actor {name:'Keanu Reeves'}),
              (carrie:Person:Actor {name:'Carrie-Anne Moss'}),
              (laurence:Person:Actor {name:'Laurence Fishburne'}),
              (leo:Person:Actor {name:'Leonardo DiCaprio'}),
              (joseph:Person:Actor {name:'Joseph Gordon-Levitt'}),
              (matthew:Person:Actor {name:'Matthew McConaughey'}),
              (nolan:Person:Director {name:'Christopher Nolan'}),
              (wachowskis:Person:Director {name:'The Wachowskis'}),

              (matrix:Movie {title:'The Matrix', released:1999}),
              (inception:Movie {title:'Inception', released:2010}),
              (interstellar:Movie {title:'Interstellar', released:2014}),

              (keanu)-[:ACTED_IN]->(matrix),
              (carrie)-[:ACTED_IN]->(matrix),
              (laurence)-[:ACTED_IN]->(matrix),

              (leo)-[:ACTED_IN]->(inception),
              (joseph)-[:ACTED_IN]->(inception),

              (matthew)-[:ACTED_IN]->(interstellar),

              (nolan)-[:DIRECTED]->(inception),
              (nolan)-[:DIRECTED]->(interstellar),
              (wachowskis)-[:DIRECTED]->(matrix);
            """
        )

        # Query the graph for the number of actors connected to each
        # movie and export the result to pandas.
        #
        # Read:
        #   (actor:Person)-[:ACTED_IN]->(movie:Movie)
        #
        # as:
        #   "find an actor `actor` and the movie `movie` they acted in."
        df = db.to_pandas(
            r"""
            MATCH (actor:Person)-[:ACTED_IN]->(movie:Movie)
            RETURN
              movie.title AS movie,
              movie.released AS released,
              count(actor) AS actor_count
            ORDER BY released
            """
        )

        print("actor counts per movie:")
        print(df)

        # Because the result is now a normal pandas DataFrame, we can
        # visualize it with matplotlib.
        ax = df.plot(
            x="movie",
            y="actor_count",
            kind="bar",
            legend=False,
            title="Actors per movie",
        )
        ax.set_xlabel("Movie")
        ax.set_ylabel("Actor count")

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()