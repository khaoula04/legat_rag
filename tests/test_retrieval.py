from rag.retrieval import rechercher_passages


def test_rechercher_passages_renvoie_des_resultats():
    question = "Quelles sont les conditions de licenciement ?"  # ← à adapter à TON corpus

    passages, distances, sources = rechercher_passages(question, k=3)

    assert len(passages) > 0
    assert len(passages) <= 3
    assert len(passages) == len(distances) == len(sources)