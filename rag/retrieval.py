import chromadb
from sentence_transformers import SentenceTransformer

DB_PATH = "./legal_rag_db"

# Connexion à la base existante
client = chromadb.PersistentClient(path=DB_PATH)
collection = client.get_collection("legal_passages")
embedder = SentenceTransformer('all-MiniLM-L6-v2')

print(f" Base chargée — {collection.count()} passages disponibles")


def rechercher_passages(question, k=3):
    question_embedding = embedder.encode([question]).tolist()

    resultats = collection.query(
        query_embeddings=question_embedding,
        n_results=k
    )

    passages_trouves = resultats["documents"][0]
    distances = resultats["distances"][0]
    #indices = [int(id) for id in resultats["ids"][0]]

    # Récupérer les sources depuis les métadonnées
    sources = resultats["metadatas"][0] if resultats["metadatas"][0] else []

    return passages_trouves, distances, sources
