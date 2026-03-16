from __future__ import annotations

"""Path matching example for the Velr Python driver.

This example shows how to match and return a path in openCypher.

Query pattern:
  MATCH p = (a:Person)-[:KNOWS]->(b:Person)-[:KNOWS]->(c:Person)
  RETURN a.name, b.name, c.name, length(p)

Meaning:
  find a path that starts at one Person node, follows a KNOWS relationship
  to a second Person node, then follows another KNOWS relationship to a
  third Person node.

`length(p)` returns the number of relationships in the path.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small graph with a chain of KNOWS relationships.
        db.run(
            r"""
            CREATE
              (frodo:Person {name:'Frodo'}),
              (sam:Person {name:'Sam'}),
              (merry:Person {name:'Merry'}),
              (pippin:Person {name:'Pippin'}),
              (frodo)-[:KNOWS]->(sam),
              (sam)-[:KNOWS]->(merry),
              (merry)-[:KNOWS]->(pippin);
            """
        )

        # Match paths of exactly two KNOWS hops.
        #
        # Read:
        #   p = (a)-[:KNOWS]->(b)-[:KNOWS]->(c)
        #
        # as:
        #   "bind the whole matched path to `p`, and also bind each node
        #    along the way to `a`, `b`, and `c`."
        with db.exec_one(
            r"""
            MATCH p = (a:Person)-[:KNOWS]->(b:Person)-[:KNOWS]->(c:Person)
            RETURN
              a.name AS from,
              b.name AS via,
              c.name AS to,
              length(p) AS hops
            ORDER BY from, via, to
            """
        ) as table:
            print("paths of two KNOWS hops:")

            with table.rows() as rows:
                for row in rows:
                    from_, via, to, hops = row
                    print(
                        f"  {from_.as_python()} -> {via.as_python()} -> "
                        f"{to.as_python()} (hops: {hops.as_python()})"
                    )


if __name__ == "__main__":
    main()