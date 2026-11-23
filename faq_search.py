
import os
from pathlib import Path

import chromadb
from dotenv import load_dotenv
from google import genai
from google.genai import types


# ---------------------------------------
# 1. Load environment variables
# ---------------------------------------

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY not found in .env file")


# ---------------------------------------
# 2. Initialize Gemini
# ---------------------------------------

gemini_client = genai.Client(api_key=API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"


# ---------------------------------------
# 3. Connect to existing ChromaDB
# ---------------------------------------

chroma_client = chromadb.PersistentClient(
    path=str(BASE_DIR / "chroma_db")
)

collection = chroma_client.get_collection(
    name="restaurant_faqs"
)


# ---------------------------------------
# 4. Generate question embedding
# ---------------------------------------

def generate_query_embedding(question):

    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=question,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_QUERY"
        )
    )

    return response.embeddings[0].values


# ---------------------------------------
# 5. Search FAQs
# ---------------------------------------

def search_faq(question, number_of_results=3):

    query_embedding = generate_query_embedding(question)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=number_of_results,
        include=["documents", "metadatas", "distances"]
    )

    faqs = []

    for metadata, distance in zip(
        results["metadatas"][0],
        results["distances"][0]
    ):

        faqs.append({
            "question": metadata["question"],
            "answer": metadata["answer"],
            "category": metadata["category"],
            "distance": distance
        })

    return faqs


# ---------------------------------------
# 6. Test the search function
# ---------------------------------------

if __name__ == "__main__":

    customer_question = "What time does your restaurant open?"

    print("\nCustomer Question:")
    print(customer_question)

    print("\nSearching FAQs...\n")

    results = search_faq(customer_question)

    for index, faq in enumerate(results, start=1):

        print(f"Result {index}")
        print("Question:", faq["question"])
        print("Answer:", faq["answer"])
        print("Category:", faq["category"])
        print("Distance:", round(faq["distance"], 4))
        print("-" * 50)
