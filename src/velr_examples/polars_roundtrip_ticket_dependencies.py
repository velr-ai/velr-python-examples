from __future__ import annotations

"""Round-trip ticket dependency data through Polars with the Velr Python driver.

This example shows how to start with tabular ticket data in Polars,
load it into Velr, model it as a graph, and export graph-derived
results back to Polars.

In this small dataset we store:

- tickets
- owners
- ticket dependencies

We then bind the Polars DataFrame as an external table and use it to
create:

- (:Ticket) nodes
- (:Person) nodes
- (:Person)-[:ASSIGNED_TO]->(:Ticket) relationships
- (:Ticket)-[:BLOCKS]->(:Ticket) relationships

This lets us move between dataframe-shaped data and graph-shaped data
in a natural way.
"""

import polars as pl
from velr.driver import Velr


def main() -> None:
    # Create a small Polars DataFrame representing ticket dependency
    # data.
    #
    # In this example:
    # - TICKET-1 is blocked by TICKET-2
    # - TICKET-2 is blocked by TICKET-3
    # - TICKET-4 has no blocker
    # - each ticket is assigned to an owner
    df = pl.DataFrame(
        {
            "key": ["TICKET-1", "TICKET-2", "TICKET-3", "TICKET-4"],
            "title": [
                "Ship embedded graph query API",
                "Finish query planner integration",
                "Stabilize runtime ABI",
                "Write Python examples",
            ],
            "status": ["Blocked", "In Progress", "Open", "Open"],
            "owner": [
                "Frodo Baggins",
                "Samwise Gamgee",
                "Gandalf",
                "Frodo Baggins",
            ],
            "blocked_by": ["TICKET-2", "TICKET-3", None, None],
        }
    )

    with Velr.open(None) as db:
        # Bind the Polars DataFrame into Velr under the logical name
        # "_tickets".
        db.bind_polars("_tickets", df)

        # Create Ticket nodes from the bound rows.
        #
        # Read:
        #   UNWIND BIND('_tickets') AS r
        #
        # as:
        #   "iterate over each bound row `r` from the external table
        #    named '_tickets'."
        db.run(
            r"""
            UNWIND BIND('_tickets') AS r
            CREATE (:Ticket {
              key: r.key,
              title: r.title,
              status: r.status
            })
            """
        )

        # Create Person nodes for ticket owners.
        db.run(
            r"""
            UNWIND BIND('_tickets') AS r
            MERGE (:Person {name: r.owner})
            """
        )

        # Connect each owner to their ticket.
        db.run(
            r"""
            UNWIND BIND('_tickets') AS r
            MATCH (owner:Person {name: r.owner})
            MATCH (ticket:Ticket {key: r.key})
            MERGE (owner)-[:ASSIGNED_TO]->(ticket)
            """
        )

        # Connect blocking tickets to blocked tickets.
        #
        # Rows where blocked_by is NULL do not create a dependency
        # edge.
        db.run(
            r"""
            UNWIND BIND('_tickets') AS r
            MATCH (blocked:Ticket {key: r.key})
            MATCH (blocker:Ticket {key: r.blocked_by})
            MERGE (blocker)-[:BLOCKS]->(blocked)
            """
        )

        # Query the graph to show blocked tickets and the owners of the
        # blocking work.
        with db.exec_one(
            r"""
            MATCH (owner:Person)-[:ASSIGNED_TO]->(blocker:Ticket)-[:BLOCKS]->(blocked:Ticket)
            RETURN
              blocked.key AS blocked_ticket,
              blocker.key AS blocker_ticket,
              owner.name AS blocker_owner
            ORDER BY blocked_ticket
            """
        ) as table:
            print("blocked tickets and the owners of the blocking work:")

            with table.rows() as rows:
                for row in rows:
                    blocked_ticket, blocker_ticket, blocker_owner = row
                    print(
                        f"  {blocked_ticket.as_python()} is blocked by "
                        f"{blocker_ticket.as_python()}, owned by "
                        f"{blocker_owner.as_python()}"
                    )

        # Export graph-derived dependency data back to Polars.
        out = db.to_polars(
            r"""
            MATCH (owner:Person)-[:ASSIGNED_TO]->(blocker:Ticket)-[:BLOCKS]->(blocked:Ticket)
            RETURN
              blocked.key AS blocked_ticket,
              blocked.status AS blocked_status,
              blocker.key AS blocker_ticket,
              owner.name AS blocker_owner
            ORDER BY blocked_ticket
            """
        )

        print()
        print("graph data exported back to Polars:")
        print(out)

        # Because the result is now a normal Polars DataFrame, we can
        # use regular dataframe operations on it.
        summary = (
            out.group_by("blocker_owner")
            .agg(pl.len().alias("blocked_ticket_count"))
            .sort("blocker_owner")
        )

        print()
        print("blocked tickets per blocker owner:")
        print(summary)


if __name__ == "__main__":
    main()