from __future__ import annotations

"""Variable-length path example for the Velr Python driver.

This example shows how to match variable-length paths in openCypher.

Query pattern:
  MATCH p = (a:Person)-[:KNOWS*1..3]->(b:Person)
  RETURN a.name, b.name, length(p)

Meaning:
  starting from one Person node, follow between 1 and 3 outgoing KNOWS
  relationships to reach another Person node.

`*1..3` means:
- at least 1 hop
- at most 3 hops

`length(p)` returns the number of relationships in the matched path.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small graph with a simple chain of KNOWS relationships.
        db.run(
            r"""
            CREATE
              (frodo:Person {name:'Frodo'}),
              (sam:Person {name:'Sam'}),
              (merry:Person {name:'Merry'}),
              (pippin:Person {name:'Pippin'}),
              (gandalf:Person {name:'Gandalf'}),
              (frodo)-[:KNOWS]->(sam),
              (sam)-[:KNOWS]->(merry),
              (merry)-[:KNOWS]->(pippin),
              (pippin)-[:KNOWS]->(gandalf);
            """
        )

        # Match paths starting from Frodo with between 1 and 3 KNOWS hops.
        with db.exec_one(
            r"""
            MATCH p = (a:Person {name:'Frodo'})-[:KNOWS*1..3]->(b:Person)
            RETURN a.name AS from, b.name AS to, length(p) AS hops
            ORDER BY hops, to
            """
        ) as table:
            print("variable-length paths from Frodo:")

            with table.rows() as rows:
                for row in rows:
                    from_, to, hops = row
                    print(f"  {from_.as_python()} -> {to.as_python()} (hops: {hops.as_python()})")


if __name__ == "__main__":
    main()