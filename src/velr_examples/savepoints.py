from __future__ import annotations

"""Savepoint examples for the Velr Python driver.

This example shows both savepoint styles supported by the Velr Python driver:

- scoped savepoints via `savepoint()`
- named savepoints via `savepoint_named(...)`

It also shows the difference between:

- rolling back a scoped savepoint
- rolling back to a named savepoint and continuing work
"""

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        # Start a transaction. All savepoints live inside a transaction.
        with db.begin_tx() as tx:
            # This write will survive because it happens before the savepoint rollback.
            tx.run("CREATE (:Temp {k:'outer'})")

            # Scoped savepoint:
            # if we roll back this savepoint, only the work done after it is undone.
            sp = tx.savepoint()
            tx.run("CREATE (:Temp {k:'inner-scoped'})")
            sp.rollback()

            # Named savepoint:
            # it remains active until explicitly released or until the transaction ends.
            tx.savepoint_named("before_named")
            tx.run("CREATE (:Temp {k:'inner-named'})")

            # Roll back to the named savepoint.
            # This removes `inner-named` but keeps the savepoint active.
            tx.rollback_to("before_named")

            # Do more work after the rollback.
            tx.run("CREATE (:Temp {k:'after-rollback'})")

            # Release the named savepoint once we no longer need it.
            tx.release_savepoint("before_named")

            # Commit the remaining work.
            tx.commit()

        # Verify what is still in the database.
        with db.exec_one(
            r"""
            MATCH (n:Temp)
            RETURN n.k AS k
            ORDER BY k
            """
        ) as table:
            print("rows after commit:")

            with table.rows() as rows:
                for row in rows:
                    (k,) = row
                    print(f"  {k.as_python()}")


if __name__ == "__main__":
    main()