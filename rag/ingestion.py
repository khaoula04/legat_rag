import fitz
import re
import os
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb

DB_PATH = "./legal_rag_db"

DOCUMENTS = {
    "GDPR": "CELEX_32016R0679_EN_TXT.pdf",
    "AI Act": "CELEX_32024R1689_EN_TXT.pdf",
    "Consumer Rights Directive": "CELEX_32011L0083_EN_TXT.pdf",
    "Digital Services Act": "CELEX_32022R2065_EN_TXT.pdf",
    "Working Time Directive": "CELEX_32003L0088_EN_TXT.pdf"
}

def extraire_articles_pdf(fichier, nom, max_articles=30):
    doc = fitz.open(fichier)
    texte_complet = ""
    for page in doc:
        texte_complet += page.get_text()

    lignes = texte_complet.split('\n')
    articles_locaux = []
    sources_locales = []

    i = 0
    while i < len(lignes):
        ligne = lignes[i].strip()
        if re.match(r'^Article\s+\d+$', ligne):
            numero = ligne
            sous_titre = lignes[i+1].strip() if i+1 < len(lignes) else ""
            contenu = sous_titre + " "
            j = i + 2
            while j < len(lignes):
                prochaine = lignes[j].strip()
                if re.match(r'^Article\s+\d+$', prochaine):
                    break
                if prochaine:
                    contenu += prochaine + " "
                j += 1
            contenu = re.sub(r'\s+', ' ', contenu).strip()
            if len(contenu.split()) > 20:
                articles_locaux.append(contenu[:1000])
                sources_locales.append(f"{numero} ({sous_titre}), {nom} — EUR-Lex")
            if len(articles_locaux) >= max_articles:
                break
        i += 1

    return articles_locaux, sources_locales


def construire_base():
    passages = []
    passages_sources = []

    print("Chargement des PDFs EUR-Lex...")
    for nom, fichier in DOCUMENTS.items():
        if not os.path.exists(fichier):
            print(f"  !!!!!!!!! {nom} — fichier introuvable !!!!!!!!!!!!!!!")
            continue
        arts, srcs = extraire_articles_pdf(fichier, nom)
        passages.extend(arts)
        passages_sources.extend(srcs)
        print(f"   {nom} — {len(arts)} articles chargés  >>>>>>>>>>>>----------")

    print(f"\n  -------------------Total : {len(passages)} passages chargés-----------------------")

    print("Chargement du modèle embedding...")
    embedder = SentenceTransformer('all-MiniLM-L6-v2')

    print("Génération des embeddings...")
    passage_embeddings = embedder.encode(passages, show_progress_bar=True)
    passage_embeddings = np.array(passage_embeddings).astype('float32')

    print("Indexation dans ChromaDB...")
    client = chromadb.PersistentClient(path=DB_PATH)
    try:
        client.delete_collection("legal_passages")
    except:
        pass

    collection = client.create_collection(
        name="legal_passages",
        metadata={"hnsw:space": "cosine"}
    )

    batch_size = 50
    for i in range(0, len(passages), batch_size):
        collection.add(
            documents=passages[i:i+batch_size],
            embeddings=passage_embeddings[i:i+batch_size].tolist(),
            ids=[str(j) for j in range(i, i+len(passages[i:i+batch_size]))],
            metadatas=[{"source": passages_sources[i+k]} for k in range(len(passages[i:i+batch_size]))]  # ← NOUVEAU
)
        print(f"  {min(i+batch_size, len(passages))}/{len(passages)} indexés...")

    print(f"\n ChromaDB prêt — {collection.count()} passages")
    print(f" Sauvegardé dans : {os.path.abspath(DB_PATH)}")


if __name__ == "__main__":
    construire_base()