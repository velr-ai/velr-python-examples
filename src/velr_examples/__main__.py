from __future__ import annotations

import importlib
import sys


EXAMPLES = [
    "basic_open",
    "basic_query",
    "query_parameters",
    "file_backed",
    "streaming_tables",
    "transaction",
    "rollback",
    "rollback_on_drop",
    "savepoints",
    "explain",
    "cypher_match",
    "cypher_where",
    "cypher_relationships",
    "cypher_aggregates",
    "cypher_unwind",
    "cypher_labels_and_properties",
    "cypher_paths",
    "cypher_var_length_paths",
    "cypher_merge",
    "cypher_merge_relationships",
    "cypher_with",
    "cypher_with_aggregates",
    "usecase_knowledge_graph",
    "usecase_fraud_detection",
    "usecase_ticket_dependencies",
    "usecase_access_control",
    "usecase_org_chart",
    "to_pandas_movies",
    "to_polars_movies",
    "to_pyarrow_movies",
    "bind_pandas_people",
    "bind_polars_people",
    "bind_arrow_people",
    "pandas_roundtrip_org_chart",
    "plotting_from_pandas_movies",
    "polars_roundtrip_ticket_dependencies",
    "plotting_from_polars_tickets",
    "table_to_pandas",
    "table_to_polars",
    "table_to_pyarrow",
    "csv_with_pandas_people",
    "csv_with_polars_ticket_dependencies",
    "fulltext_search",
    "vector_embeddings_fastembed",

]


def print_help() -> None:
    print("Usage:")
    print("  python -m velr_examples list")
    print("  python -m velr_examples <example_name>")
    print()
    print("Examples:")
    for name in EXAMPLES:
        print(f"  {name}")


def main() -> int:
    argv = sys.argv[1:]

    if not argv or argv[0] in {"-h", "--help", "help"}:
        print_help()
        return 0

    cmd = argv[0]

    if cmd == "list":
        for name in EXAMPLES:
            print(name)
        return 0

    if cmd not in EXAMPLES:
        print(f"Unknown example: {cmd}", file=sys.stderr)
        print(file=sys.stderr)
        print("Run `python -m velr_examples list` to see available examples.", file=sys.stderr)
        return 2

    module = importlib.import_module(f"velr_examples.{cmd}")
    fn = getattr(module, "main", None)

    if fn is None:
        print(f"Example module velr_examples.{cmd} has no main()", file=sys.stderr)
        return 2

    fn()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
