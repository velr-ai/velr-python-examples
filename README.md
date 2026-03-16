# velr-python-examples

Examples showing how to use the [Velr](https://velr.ai/) Python driver.

Velr is an embedded property-graph database built in Rust, backed by SQLite, and queried with openCypher. This repository contains small, focused Python examples that demonstrate common patterns when working with the Velr Python API.

The goal of this repository is to help users quickly install Velr from PyPI, run simple examples, and explore common graph workflows in Python.

## What this repo contains

Examples in this repository cover:

- opening in-memory and file-backed databases
- creating and querying graph data
- reading result tables row by row
- converting typed values to normal Python objects
- streaming multiple result tables
- using transactions, rollbacks, and savepoints
- inspecting query plans with `explain()`
- working with openCypher concepts such as `MATCH`, `WHERE`, `MERGE`, `WITH`, paths, and variable-length paths
- modeling real-world graph use cases such as knowledge graphs, fraud detection, access control, org charts, and ticket dependencies
- exporting query results to pandas, Polars, and PyArrow
- converting existing result tables to pandas, Polars, and PyArrow
- binding pandas, Polars, and PyArrow data into Velr with `UNWIND BIND(...)`
- reading CSV data with pandas or Polars and turning it into graph data
- plotting graph-derived data with pandas or Polars and matplotlib

## Getting started

Clone the repository and create a virtual environment:

```bash
git clone https://github.com/velr-ai/velr-python-examples.git
cd velr-python-examples

python3.12 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -e .
````

Velr itself is installed from PyPI as a normal dependency of this examples repository.

To run examples that use optional libraries, install the extras you need:

```bash
pip install -e '.[arrow]'
pip install -e '.[pandas]'
pip install -e '.[polars]'
pip install -e '.[plotting]'
```

Plotting examples also require the dataframe stack they use:

```bash
pip install -e '.[pandas,plotting]'
pip install -e '.[polars,plotting]'
```

To install everything used by the examples:

```bash
pip install -e '.[all]'
```

This repository targets the Python versions supported by Velr:

* Python 3.12
* Python 3.13

## Running examples

The easiest way to run examples is through the bundled CLI.

List the available examples:

```bash
velr-examples list
```

Run a specific example:

```bash
velr-examples basic_query
```

You can also run examples via `python -m`:

```bash
python -m velr_examples list
python -m velr_examples basic_query
python -m velr_examples.file_backed
```

## Example layout

Examples mirror the structure of the Rust examples repository where that makes sense, while keeping the code idiomatic for Python.

### Core driver examples

* `basic_open.py`
* `basic_query.py`
* `file_backed.py`
* `streaming_tables.py`
* `transaction.py`
* `rollback.py`
* `rollback_on_drop.py`
* `savepoints.py`
* `explain.py`

### openCypher examples

* `cypher_match.py`
* `cypher_where.py`
* `cypher_relationships.py`
* `cypher_aggregates.py`
* `cypher_unwind.py`
* `cypher_labels_and_properties.py`
* `cypher_paths.py`
* `cypher_var_length_paths.py`
* `cypher_merge.py`
* `cypher_merge_relationships.py`
* `cypher_with.py`
* `cypher_with_aggregates.py`

### Use case examples

* `usecase_knowledge_graph.py`
* `usecase_fraud_detection.py`
* `usecase_ticket_dependencies.py`
* `usecase_access_control.py`
* `usecase_org_chart.py`

### Dataframe, Arrow, CSV, and plotting examples

#### Export query results

* `to_pandas_movies.py`
* `to_polars_movies.py`
* `to_pyarrow_movies.py`

#### Convert an existing result table

* `table_to_pandas.py`
* `table_to_polars.py`
* `table_to_pyarrow.py`

#### Bind external dataframe or Arrow data

* `bind_pandas_people.py`
* `bind_polars_people.py`
* `bind_arrow_people.py`

#### Round-trip dataframe workflows

* `pandas_roundtrip_org_chart.py`
* `polars_roundtrip_ticket_dependencies.py`

#### CSV-based workflows

* `csv_with_pandas_people.py`
* `csv_with_polars_ticket_dependencies.py`

#### Plotting workflows

* `plotting_from_pandas_movies.py`
* `plotting_from_polars_tickets.py`

## Minimal example

```python
from __future__ import annotations

from velr.driver import Velr


def main() -> None:
    with Velr.open(None) as db:
        db.run("CREATE (:Person {name:'Keanu Reeves', born:1964})")

        with db.exec_one(
            "MATCH (p:Person) RETURN p.name AS name, p.born AS born"
        ) as table:
            with table.rows() as rows:
                for row in rows:
                    name, born = row
                    print(f"name={name.as_python()}")
                    print(f"born={born.as_python()}")


if __name__ == "__main__":
    main()
```

## Python style

These examples are intentionally written in a Pythonic style.

They generally prefer:

* `with` blocks for connections, tables, streams, and transactions
* `Cell.as_python()` for converting values to ordinary Python objects
* straightforward scripts with a small `main()` function
* pandas, Polars, and PyArrow helpers where appropriate

The examples aim to stay conceptually close to the Rust examples while still feeling natural to Python users.

## Dataframe and Arrow workflows

The dataframe and Arrow examples show both directions of integration:

* graph data exported from Velr into pandas, Polars, or PyArrow
* external pandas, Polars, Arrow, or CSV data bound into Velr and turned into graph data

These examples are about interoperability and workflow clarity rather than minimal startup time. For very small datasets, Python import overhead from libraries such as pandas, Polars, PyArrow, or matplotlib can dominate total runtime.


## Related links

* [Velr](https://velr.ai/)
* [Velr Python Documentation](https://velr.ai/docs/python-driver/)
* [Velr on PyPI](https://pypi.org/project/velr/)
* [velr-rust-examples](https://github.com/velr-ai/velr-rust-examples)

## License

This repository is licensed under the MIT License. See [`LICENSE`](LICENSE).
