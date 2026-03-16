from __future__ import annotations

"""Ticket dependency example for the Velr Python driver.

This example shows how a graph can model ticket dependencies.

In this small graph we store:

- tickets
- people

and connect them with relationships such as:

- (:Ticket)-[:BLOCKS]->(:Ticket)
- (:Person)-[:ASSIGNED_TO]->(:Ticket)

This lets us ask questions like:

- Which tickets are blocked by other tickets?
- Who is assigned to the blocking work?
- What dependency chains exist across a set of tickets?
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small ticket graph.
        #
        # In this example:
        # - TICKET-1 is blocked by TICKET-2
        # - TICKET-2 is blocked by TICKET-3
        # - each ticket is assigned to a person
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
                title:'Write Rust driver examples',
                status:'Open'
              }),

              (frodo)-[:ASSIGNED_TO]->(t1),
              (sam)-[:ASSIGNED_TO]->(t2),
              (gandalf)-[:ASSIGNED_TO]->(t3),
              (frodo)-[:ASSIGNED_TO]->(t4),

              (t2)-[:BLOCKS]->(t1),
              (t3)-[:BLOCKS]->(t2);
            """
        )

        # Find tickets that are blocked by other tickets.
        #
        # Read:
        #   (blocker:Ticket)-[:BLOCKS]->(blocked:Ticket)
        #
        # as:
        #   "ticket `blocker` blocks ticket `blocked`."
        with db.exec_one(
            r"""
            MATCH (blocker:Ticket)-[:BLOCKS]->(blocked:Ticket)
            RETURN
              blocked.key AS blocked_ticket,
              blocked.title AS blocked_title,
              blocker.key AS blocker_ticket,
              blocker.title AS blocker_title
            ORDER BY blocked_ticket
            """
        ) as table:
            print("blocked tickets:")

            with table.rows() as rows:
                for row in rows:
                    blocked_ticket, blocked_title, blocker_ticket, blocker_title = row
                    print(
                        f"  {blocked_ticket.as_python()} "
                        f"({blocked_title.as_python()})"
                    )
                    print(
                        f"    blocked by {blocker_ticket.as_python()} "
                        f"({blocker_title.as_python()})"
                    )

        # Find who is assigned to the blocking ticket.
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
            print()
            print("owners of blocking tickets:")

            with table.rows() as rows:
                for row in rows:
                    blocked_ticket, blocker_ticket, blocker_owner = row
                    print(
                        f"  {blocked_ticket.as_python()} is blocked by "
                        f"{blocker_ticket.as_python()}, owned by "
                        f"{blocker_owner.as_python()}"
                    )

        # Follow a dependency chain of variable length.
        #
        # Read:
        #   (start:Ticket)<-[:BLOCKS*1..3]-(upstream:Ticket)
        #
        # as:
        #   "find upstream tickets that block `start` through a chain
        #    of between 1 and 3 BLOCKS relationships."
        with db.exec_one(
            r"""
            MATCH p = (start:Ticket {key:'TICKET-1'})<-[:BLOCKS*1..3]-(upstream:Ticket)
            RETURN
              start.key AS ticket,
              upstream.key AS upstream_ticket,
              length(p) AS dependency_hops
            ORDER BY dependency_hops, upstream_ticket
            """
        ) as table:
            print()
            print("dependency chain for TICKET-1:")

            with table.rows() as rows:
                for row in rows:
                    ticket, upstream_ticket, dependency_hops = row
                    print(
                        f"  {ticket.as_python()} depends on "
                        f"{upstream_ticket.as_python()} "
                        f"({dependency_hops.as_python()} hop(s) away)"
                    )


if __name__ == "__main__":
    main()