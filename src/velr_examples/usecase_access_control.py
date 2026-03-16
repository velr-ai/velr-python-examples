from __future__ import annotations

"""Access control example for the Velr Python driver.

This example shows how a graph can model access control.

In this small graph we store:

- users
- roles
- teams
- resources

and connect them with relationships such as:

- (:User)-[:MEMBER_OF]->(:Team)
- (:Team)-[:HAS_ROLE]->(:Role)
- (:User)-[:HAS_ROLE]->(:Role)
- (:Role)-[:CAN_ACCESS]->(:Resource)

This lets us ask questions like:

- Which resources can a user access directly?
- Which resources can a user access through team membership?
- Why does a user have access to a given resource?

Graphs are useful here because permissions often come from several
connected sources at once: direct roles, team roles, and shared resources.
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Create a small access-control graph.
        #
        # In this example:
        # - Frodo is in the Platform team
        # - Sam is in the Support team
        # - Gandalf has a direct Admin role
        # - teams and users gain access through roles
        db.run(
            r"""
            CREATE
              (frodo:User {name:'Frodo'}),
              (sam:User {name:'Sam'}),
              (gandalf:User {name:'Gandalf'}),

              (platform:Team {name:'Platform'}),
              (support:Team {name:'Support'}),

              (reader:Role {name:'Reader'}),
              (operator:Role {name:'Operator'}),
              (admin:Role {name:'Admin'}),

              (docs:Resource {name:'Docs'}),
              (dashboard:Resource {name:'Operations Dashboard'}),
              (prod:Resource {name:'Production Cluster'}),
              (billing:Resource {name:'Billing Console'}),

              (frodo)-[:MEMBER_OF]->(platform),
              (sam)-[:MEMBER_OF]->(support),

              (platform)-[:HAS_ROLE]->(operator),
              (support)-[:HAS_ROLE]->(reader),

              (gandalf)-[:HAS_ROLE]->(admin),

              (reader)-[:CAN_ACCESS]->(docs),

              (operator)-[:CAN_ACCESS]->(docs),
              (operator)-[:CAN_ACCESS]->(dashboard),

              (admin)-[:CAN_ACCESS]->(docs),
              (admin)-[:CAN_ACCESS]->(dashboard),
              (admin)-[:CAN_ACCESS]->(prod),
              (admin)-[:CAN_ACCESS]->(billing);
            """
        )

        # Find resources a user can access through team membership.
        #
        # Read:
        #   (u:User)-[:MEMBER_OF]->(t:Team)-[:HAS_ROLE]->(r:Role)-[:CAN_ACCESS]->(res:Resource)
        #
        # as:
        #   "the user belongs to a team, the team has a role,
        #    and that role grants access to a resource."
        with db.exec_one(
            r"""
            MATCH (u:User)-[:MEMBER_OF]->(t:Team)-[:HAS_ROLE]->(r:Role)-[:CAN_ACCESS]->(res:Resource)
            RETURN
              u.name AS user,
              t.name AS team,
              r.name AS role,
              res.name AS resource
            ORDER BY user, resource
            """
        ) as table:
            print("access granted through team membership:")

            with table.rows() as rows:
                for row in rows:
                    user, team, role, resource = row
                    print(
                        f"  {user.as_python()} -> {team.as_python()} -> "
                        f"{role.as_python()} -> {resource.as_python()}"
                    )

        # Find resources a user can access directly through their own role.
        with db.exec_one(
            r"""
            MATCH (u:User)-[:HAS_ROLE]->(r:Role)-[:CAN_ACCESS]->(res:Resource)
            RETURN
              u.name AS user,
              r.name AS role,
              res.name AS resource
            ORDER BY user, resource
            """
        ) as table:
            print()
            print("access granted through direct user roles:")

            with table.rows() as rows:
                for row in rows:
                    user, role, resource = row
                    print(
                        f"  {user.as_python()} -> {role.as_python()} -> "
                        f"{resource.as_python()}"
                    )

        # Combine both access paths and explain why Frodo can access each resource.
        with db.exec_one(
            r"""
            MATCH (u:User {name:'Frodo'})-[:MEMBER_OF]->(t:Team)-[:HAS_ROLE]->(r:Role)-[:CAN_ACCESS]->(res:Resource)
            RETURN
              u.name AS user,
              res.name AS resource,
              t.name AS via_team,
              r.name AS via_role
            ORDER BY resource
            """
        ) as table:
            print()
            print("why Frodo has access:")

            with table.rows() as rows:
                for row in rows:
                    user, resource, via_team, via_role = row
                    print(
                        f"  {user.as_python()} can access {resource.as_python()} "
                        f"via team {via_team.as_python()} and role {via_role.as_python()}"
                    )


if __name__ == "__main__":
    main()