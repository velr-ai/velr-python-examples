from __future__ import annotations

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        db.run("CREATE (:Person {name:'Keanu Reeves', born:1964})")

        with db.exec_one(
            "MATCH (p:Person) RETURN p.name AS name, p.born AS born"
        ) as table:
            print(table.column_names())

            with table.rows() as rows:
                for row in rows:
                    name, born = row
                    print(f"name={name.as_python()}")
                    print(f"born={born.as_python()}")


if __name__ == "__main__":
    main()