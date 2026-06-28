from __future__ import annotations

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        db.run(
            "CREATE (:Person {name: $name, role: $role, age: $age})",
            params={"name": "Ada Lovelace", "role": "researcher", "age": 36},
        )
        db.run(
            "CREATE (:Person {name: $name, role: $role, age: $age})",
            params={"name": "Grace Hopper", "role": "engineer", "age": 85},
        )

        # This stays a string value; it is not interpolated into the Cypher text.
        db.run(
            "CREATE (:Person {name: $name, role: $role, age: $age})",
            params={
                "name": "Alice') MATCH (n) RETURN n //",
                "role": "researcher",
                "age": 42,
            },
        )

        with db.exec_one(
            """
            MATCH (p:Person)
            WHERE p.role = $role AND p.age >= $min_age
            RETURN p.name AS name, p.age AS age
            ORDER BY age, name
            """,
            max_result_rows=10,
            params={"role": "researcher", "min_age": 30},
        ) as table:
            print("researchers aged at least 30:")
            with table.rows() as rows:
                for row in rows:
                    name, age = row
                    print(f"  {name.as_python()} ({age.as_python()})")


if __name__ == "__main__":
    main()
