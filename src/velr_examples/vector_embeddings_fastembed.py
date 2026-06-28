from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

from fastembed import TextEmbedding
from velr.driver import Velr, VectorEmbeddingInput


def input_text(input: VectorEmbeddingInput) -> str:
    return "\n".join(
        str(field.value)
        for field in input.fields
        if field.value_type == "string"
    )


def main() -> None:
    # BAAI/bge-small-en-v1.5 is a small 384-dimensional text embedding model.
    # The first run downloads the model into FastEmbed's normal cache.
    model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")

    def embedder(inputs: list[VectorEmbeddingInput]) -> list[list[float]]:
        documents = [input_text(input) for input in inputs]
        return [vector.tolist() for vector in model.embed(documents)]

    with TemporaryDirectory() as tmp:
        db_path = Path(tmp) / "vector_embeddings.db"

        # Vector indexes use sidecar storage, so they need a file-backed DB.
        with Velr.open(str(db_path)) as db:
            db.register_vector_embedder("fastembed", embedder)

            db.run(
                """
                CREATE VECTOR INDEX paperEmbedding IF NOT EXISTS
                FOR (n:Paper)
                ON EACH [n.title, n.abstract]
                OPTIONS {
                  indexConfig: {
                    dimensions: 384,
                    metric: 'cosine',
                    embedder: 'fastembed'
                  }
                }
                """
            )

            # The index is maintained by normal writes. There is no separate
            # "add this vector" bookkeeping step.
            db.run(
                """
                CREATE
                  (:Paper {
                    id: 'p1',
                    title: 'Graph Search with Python',
                    abstract: 'Index nodes and relationships with openCypher'
                  }),
                  (:Paper {
                    id: 'p2',
                    title: 'Greek Letters in Graph Search',
                    abstract: 'Alpha, beta, and gamma examples for retrieval'
                  }),
                  (:Paper {
                    id: 'p3',
                    title: 'Local Embeddings',
                    abstract: 'Run compact embedding models inside an application'
                  })
                """
            )

            db.run(
                """
                MATCH (p:Paper {id: 'p2'})
                SET p.abstract = p.abstract + ' with semantic vector search'
                """
            )

            with db.exec_one(
                """
                CALL db.index.vector.queryNodes(
                    'paperEmbedding',
                    3,
                    'paper about greek letters'
                )
                YIELD node, score
                RETURN node, score
                """
            ) as table:
                print("nearest papers:")
                with table.rows() as rows:
                    for row in rows:
                        node, score = row
                        print(f"  node={node.as_python()} score={score.as_python():.3f}")


if __name__ == "__main__":
    main()
