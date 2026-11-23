
import os
import json
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
    raise ValueError(
        "GEMINI_API_KEY not found. Please check your .env file."
    )


# ---------------------------------------
# 2. Initialize Gemini client
# ---------------------------------------

gemini_client = genai.Client(api_key=API_KEY)

EMBEDDING_MODEL = "gemini-embedding-001"


# ---------------------------------------
# 3. Initialize ChromaDB
# ---------------------------------------

chroma_client = chromadb.PersistentClient(
    path=str(BASE_DIR / "chroma_db")
)

collection = chroma_client.get_or_create_collection(
    name="restaurant_faqs",
    metadata={"hnsw:space": "cosine"}
)


# ---------------------------------------
# 4. Load FAQs from JSON file
# ---------------------------------------

faq_file = BASE_DIR / "faqs.json"

with open(faq_file, "r", encoding="utf-8") as file:
    faqs = json.load(file)

print(f"Total FAQs loaded: {len(faqs)}")


# ---------------------------------------
# 5. Generate embeddings
# ---------------------------------------

def generate_embedding(text):

    response = gemini_client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(
            task_type="RETRIEVAL_DOCUMENT",
            title="The Gourmet Table Restaurant FAQ"
        )
    )

    return response.embeddings[0].values


# ---------------------------------------
# 6. Store FAQs in ChromaDB
# ---------------------------------------

for faq in faqs:

    faq_id = f"faq_{faq['id']}"

    question = faq["question"]
    answer = faq["answer"]
    category = faq["category"]

    # Combine question and answer into one document
    document = f"Question: {question}\nAnswer: {answer}"

    print(f"Processing: {question}")

    # Generate numerical embedding
    embedding = generate_embedding(document)

    # Store document, embedding and metadata
    collection.upsert(
        ids=[faq_id],
        embeddings=[embedding],
        documents=[document],
        metadatas=[
            {
                "question": question,
                "answer": answer,
                "category": category
            }
        ]
    )


# ---------------------------------------
# 7. Display final results
# ---------------------------------------

print("\n================================")
print("FAQ INGESTION COMPLETED")
print("================================")

print("Total FAQs in JSON:", len(faqs))
print("Total FAQs in ChromaDB:", collection.count())

print("Database location:", BASE_DIR / "chroma_db")

print("\nAll FAQs successfully stored!")
