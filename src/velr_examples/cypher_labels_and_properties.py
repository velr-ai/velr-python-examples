from __future__ import annotations

"""Label and property inspection example for the Velr Python driver.

This example shows how to inspect labels and properties in openCypher.

Functions used:
  labels(n)      -> list of labels on a node
  keys(n)        -> list of property names on a node
  properties(n)  -> map of all properties on a node

Meaning:
  instead of only reading one property like `p.name`, these functions let
  you inspect the shape of a node itself.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small graph with labeled nodes and a few properties.
        db.run(
            r"""
            CREATE
              (:Person:Actor {name:'Keanu Reeves', born:1964}),
              (:Person:Actor {name:'Carrie-Anne Moss', born:1967}),
              (:Movie:ScienceFiction {title:'The Matrix', released:1999});
            """
        )

        # Match Person nodes and inspect:
        # - their labels
        # - their property keys
        # - their full property map
        #
        # `labels(...)`, `keys(...)`, and `properties(...)` typically come back
        # as JSON-like values, so we parse them as Python values for display.
        with db.exec_one(
            r"""
            MATCH (p:Person)
            RETURN
              p.name AS name,
              labels(p) AS labels,
              keys(p) AS keys,
              properties(p) AS props
            ORDER BY name
            """
        ) as table:
            print("person nodes:")

            with table.rows() as rows:
                for row in rows:
                    name, labels, keys, props = row

                    print(f"  name:   {name.as_python()}")
                    print(f"  labels: {labels.as_python(parse_json=True)}")
                    print(f"  keys:   {keys.as_python(parse_json=True)}")
                    print(f"  props:  {props.as_python(parse_json=True)}")
                    print()


if __name__ == "__main__":
    main()