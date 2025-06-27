# agents/classifier_agent.py

import chardet
from typing import TypedDict, Literal
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from astrapy import DataAPIClient
import os
from backend.utils.embeddings import get_text_embedding
from backend.utils.file_reader import read_file_safely
from backend.config import main as config

# Document type categories
Categories = Literal[
    "medical_license", "medical_degree", "training_certificate", "board_certificate", "not_a_valid_credential"
]


# State definition
class ClassifierState(TypedDict):
    file_path: str
    document_type: Categories
    file_content: str
    context: str


def embed_and_search(state: ClassifierState) -> dict:
    file_path = state["file_path"]

    try:
        content = read_file_safely(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read file: {file_path}. Reason: {e}")

    embedding = get_text_embedding(content)

    client = DataAPIClient(config.ASTRA_DB_SECRET_KEY)
    db = client.get_database_by_api_endpoint(
        config.ASTRA_DB_ENDPOINT, keyspace=config.ASTRA_DB_KEYSPACE
    )
    collection = db.get_collection("embeddings")

    results = collection.find({}, sort={"$vector": embedding}, limit=5)
    similar_context = "\n---\n".join(r["text"] for r in results if "text" in r)

    new_state = dict(state)
    new_state.update(
        {
            "file_content": content,
            "context": similar_context,
        }
    )

    return new_state


# Step 2: Classify document type using Gemini
def classify_document(state: dict) -> ClassifierState:

    content = state["file_content"]
    context = state["context"]

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest", google_api_key=config.GEMINI_API_KEY
    )

    prompt = f"""Classify the type of this medical document into one of the following:
- medical_license
- medical_degree
- training_certificate
- board_certificate

If its not a valid medical document or else it doesn't match with those 4 classification types then mark it as
- not_a_valid_credential

Document:
\"\"\"
{content}
\"\"\"

Similar documents for context:
\"\"\"
{context}
\"\"\"

Respond with only the type name from the list."""

    response = llm.invoke(prompt)
    label = response.content.strip().lower()

    valid_labels = {
        "medical_license",
        "medical_degree",
        "training_certificate",
        "board_certificate",
    }

    if label not in valid_labels:
        raise ValueError(f"Unexpected classification output: {label}")

    return {"file_path": state["file_path"], "document_type": label}


# Step 3: Format result for output
def format_output(state: ClassifierState) -> dict:
    return {"type": state["document_type"]}


# Build the LangGraph classifier agent
def build_classifier_agent():
    graph = StateGraph(ClassifierState)
    graph.add_node("EmbedAndRetrieve", embed_and_search)
    graph.add_node("Classify", classify_document)
    graph.add_node("Format", format_output)

    graph.set_entry_point("EmbedAndRetrieve")
    graph.add_edge("EmbedAndRetrieve", "Classify")
    graph.add_edge("Classify", "Format")
    graph.set_finish_point("Format")

    return graph.compile()


# For testing or running directly
async def classify_file(file_path: str) -> dict:
    graph = build_classifier_agent()
    result = await graph.ainvoke({"file_path": file_path})
    return result
