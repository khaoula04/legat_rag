import requests
from rag.retrieval import rechercher_passages

def repondre(question):
    # Étape 1 : récupérer les passages pertinents depuis ChromaDB
    passages_trouves, distances, sources = rechercher_passages(question, k=3)
    
    # Étape 2 : combiner les passages en un seul contexte
    contexte = "\n\n".join(passages_trouves)
    source_principale = sources[0]["source"] if sources else "Unknown"

    # Étape 3 : construire le prompt pour Phi-3
    # On lui dit explicitement de ne répondre qu'à partir du contexte
    prompt = f"""You are a strict legal assistant specializing in EU law.
Answer the question based ONLY on the context below.
If the context is partially relevant, extract what is useful.
Only say "This topic is not covered" if the context is completely unrelated.
Be concise and precise.

Context:
{contexte}

Question: {question}

Answer:"""

    # Étape 4 : envoyer à Phi-3 via Ollama (qui tourne en local)
    response = requests.post(
        "http://localhost:11434/api/generate",
        json={"model": "phi3", "prompt": prompt, "stream": False}
    )

    reponse_text = response.json()["response"].strip()

    return {
        "question": question,
        "reponse": reponse_text,
        "source": f" {source_principale}",
        "contexte": contexte[:300] + "..."
    }