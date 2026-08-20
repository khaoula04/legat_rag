import gradio as gr
from rag.generation import repondre
from rag.ingestion import construire_base
import os

# Si la base n'existe pas encore, on la construit automatiquement
if not os.path.exists("./legal_rag_db"):
    print("Base introuvable — construction en cours...")
    construire_base()

# Fonction qui connecte Gradio à notre pipeline

def chatbot_legal(question):
    if not question.strip():
        return "Please enter a question.", "", ""
    try:
        res = repondre(question)
        return res["reponse"], res["source"], res["contexte"]
    except Exception as e:
        return f"Error: {str(e)}", "", ""


# Interface Gradio
interface = gr.Interface(
    fn=chatbot_legal,
    inputs=gr.Textbox(
        label="Legal question",
        placeholder="Ex: What does GDPR protect? What are my rights as a consumer?"
    ),
    outputs=[
        gr.Textbox(label="Answer"),
        gr.Textbox(label="Source"),
        gr.Textbox(label="Passage used")
    ],
    title="Legal RAG System — Powered by Phi-3",
    description="Ask any question about EU law. Answers are grounded in official EUR-Lex documents."
)

if __name__ == "__main__":
    interface.launch()
    