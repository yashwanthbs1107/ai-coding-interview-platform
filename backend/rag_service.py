from pathlib import Path
from google import genai
from pinecone import Pinecone
import os
from dotenv import load_dotenv

load_dotenv()

KNOWLEDGE_DIR = Path(__file__).parent / "knowledge"

gemini_client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)

pinecone = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pinecone.Index("ai-coding-rag")


def load_documents():
    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.txt"):
        content = file_path.read_text(encoding="utf-8")

        documents.append({
            "filename": file_path.name,
            "content": content
        })

    return documents


def chunk_text(text):
    sections = text.split("\n\n")

    chunks = []

    for section in sections:
        section = section.strip()

        if section:
            chunks.append(section)

    return chunks


def create_embedding(text):
    response = gemini_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config={
            "output_dimensionality": 768
        }
    )

    return response.embeddings[0].values



def store_documents():
    documents = load_documents()

    vectors = []

    vector_id = 0

    for document in documents:
        chunks = chunk_text(document["content"])

        for chunk in chunks:
            embedding = create_embedding(chunk)

            vectors.append({
                "id": f"{document['filename']}-{vector_id}",
                "values": embedding,
                "metadata": {
                    "text": chunk,
                    "source": document["filename"]
                }
            })

            vector_id += 1

    index.upsert(vectors=vectors)

    return len(vectors)

def search_knowledge(query, top_k=3):
    query_embedding = create_embedding(query)

    results = index.query(
        vector=query_embedding,
        top_k=top_k,
        include_metadata=True
    )

    return results


def get_rag_context(query, top_k=3):
    results = search_knowledge(query, top_k)

    context = []

    for match in results["matches"]:
        text = match["metadata"]["text"]
        context.append(text)

    return "\n\n".join(context)