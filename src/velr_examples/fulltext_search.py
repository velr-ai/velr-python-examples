from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from velr.driver import Velr


def main() -> None:
    with TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "fulltext_search.db"

        # Full-text indexes use sidecar storage, so they need a file-backed DB.
        with Velr.open(str(db_path)) as db:
            db.run(
                """
                CREATE
                  (:Paper {
                    id: 'p1',
                    title: 'Graph Search with Python',
                    abstract: 'A practical tour of graph retrieval and indexing'
                  }),
                  (:Paper {
                    id: 'p2',
                    title: 'Vector Embeddings for Local Apps',
                    abstract: 'Semantic retrieval with compact embedding models'
                  }),
                  (:Paper {
                    id: 'p3',
                    title: 'Greek Letters in Scientific Papers',
                    abstract: 'Alpha, beta, and gamma notation in research writing'
                  })
                """
            )

            db.run(
                """
                CREATE FULLTEXT INDEX paperText IF NOT EXISTS
                FOR (n:Paper)
                ON EACH [n.title, n.abstract]
                """
            )

            print("full-text search for title:graph OR abstract:embedding")
            with db.exec_one(
                """
                CALL db.index.fulltext.queryNodes(
                    'paperText',
                    'title:graph OR abstract:embedding'
                )
                YIELD node, score
                RETURN node, score
                """
            ) as table:
                with table.rows() as rows:
                    for row in rows:
                        node, score = row
                        print(f"  node={node.as_python()} score={score.as_python():.3f}")

            # Writes keep the full-text index current. No manual reindex call is needed.
            db.run(
                """
                MATCH (p:Paper {id: 'p3'})
                SET p.abstract = 'Greek letters used in graph embeddings and search examples'
                """
            )

            print()
            print("after updating p3.abstract:")
            with db.exec_one(
                """
                CALL db.index.fulltext.queryNodes('paperText', 'abstract:embeddings')
                YIELD node, score
                RETURN node, score
                """
            ) as table:
                with table.rows() as rows:
                    for row in rows:
                        node, score = row
                        print(f"  node={node.as_python()} score={score.as_python():.3f}")


if __name__ == "__main__":
    main()
