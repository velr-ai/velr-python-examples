from __future__ import annotations

from velr.driver import Velr


def main() -> None:
    # Open an in-memory database and seed a little data.
    with Velr.open(None) as db:
        db.run(
            r"""
            CREATE
              (:Movie {title:'The Matrix', released:1999}),
              (:Movie {title:'Inception', released:2010});
            """
        )

        # `exec()` can return multiple result tables when the Cypher text
        # contains multiple statements.
        with db.exec(
            r"""
            MATCH (m:Movie {title:'The Matrix'})
            RETURN m.title AS title;

            MATCH (m:Movie {title:'Inception'})
            RETURN m.released AS released;
            """
        ) as stream:
            table_no = 0

            # Pull result tables one by one until the stream is exhausted.
            while True:
                table = stream.next_table()
                if table is None:
                    break

                table_no += 1
                with table:
                    print(f"table #{table_no}")
                    print(f"columns: {table.column_names()}")

                    # Each table can then be iterated row by row.
                    with table.rows() as rows:
                        for row in rows:
                            for i, cell in enumerate(row):
                                value = cell.as_python(parse_json=False)
                                if value is None:
                                    print(f"  col[{i}] = null")
                                else:
                                    print(f"  col[{i}] = {value}")

                    print()


if __name__ == "__main__":
    main()