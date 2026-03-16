from __future__ import annotations

from velr.driver import Velr


def main() -> None:
    # Open an in-memory database.
    with Velr.open(None) as db:
        # Build an explain trace for a Cypher query.
        #
        # `explain()` plans the query and returns structured trace data,
        # but does not execute the query itself.
        with db.explain(
            r"""
            MATCH (n) RETURN n
            """
        ) as trace:
            # Print how many top-level plans are present in the trace.
            print(f"plans: {trace.plan_count()}")

            # Render the trace in its compact human-readable form.
            print()
            print(trace.to_compact_string())


if __name__ == "__main__":
    main()