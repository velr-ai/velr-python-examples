from __future__ import annotations

"""Plot graph-derived ticket data with Polars and matplotlib.

This example shows how to query ticket dependency data from Velr,
materialize the result as a Polars DataFrame, and visualize it with
matplotlib.

In this small graph we store:

- tickets
- people

and connect them with relationships such as:

- (:Ticket)-[:BLOCKS]->(:Ticket)
- (:Person)-[:ASSIGNED_TO]->(:Ticket)

This lets us use Velr for graph-shaped dependency data and standard
Python tools for dataframe analysis and plotting.
"""

try:
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit(
        "This example requires matplotlib.\n"
        "Install it with: pip install matplotlib"
    ) from exc

import polars as pl
from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small ticket graph.
        #
        # In this example:
        # - TICKET-1 is blocked by TICKET-2
        # - TICKET-2 is blocked by TICKET-3
        # - TICKET-4 is blocked by TICKET-2
        # - each blocking ticket is assigned to a person
        db.run(
            r"""
            CREATE
              (frodo:Person {name:'Frodo Baggins'}),
              (sam:Person {name:'Samwise Gamgee'}),
              (gandalf:Person {name:'Gandalf'}),

              (t1:Ticket {
                key:'TICKET-1',
                title:'Ship embedded graph query API',
                status:'Blocked'
              }),
              (t2:Ticket {
                key:'TICKET-2',
                title:'Finish query planner integration',
                status:'In Progress'
              }),
              (t3:Ticket {
                key:'TICKET-3',
                title:'Stabilize runtime ABI',
                status:'Open'
              }),
              (t4:Ticket {
                key:'TICKET-4',
                title:'Write Python examples',
                status:'Blocked'
              }),

              (frodo)-[:ASSIGNED_TO]->(t1),
              (sam)-[:ASSIGNED_TO]->(t2),
              (gandalf)-[:ASSIGNED_TO]->(t3),
              (frodo)-[:ASSIGNED_TO]->(t4),

              (t2)-[:BLOCKS]->(t1),
              (t3)-[:BLOCKS]->(t2),
              (t2)-[:BLOCKS]->(t4);
            """
        )

        # Query the graph for the number of blocked tickets owned by
        # each person and export the result to Polars.
        #
        # Read:
        #   (owner:Person)-[:ASSIGNED_TO]->(blocker:Ticket)-[:BLOCKS]->(blocked:Ticket)
        #
        # as:
        #   "find the owner `owner` of a blocking ticket `blocker`
        #    and the blocked ticket `blocked`."
        df = db.to_polars(
            r"""
            MATCH (owner:Person)-[:ASSIGNED_TO]->(blocker:Ticket)-[:BLOCKS]->(blocked:Ticket)
            RETURN
              owner.name AS blocker_owner,
              count(blocked) AS blocked_ticket_count
            ORDER BY blocker_owner
            """
        )

        print("blocked tickets per blocker owner:")
        print(df)

        # Because the result is now a normal Polars DataFrame, we can
        # visualize it with matplotlib.
        owners = df["blocker_owner"].to_list()
        counts = df["blocked_ticket_count"].to_list()

        fig, ax = plt.subplots()
        ax.bar(owners, counts)
        ax.set_title("Blocked tickets per blocker owner")
        ax.set_xlabel("Owner")
        ax.set_ylabel("Blocked ticket count")

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    main()