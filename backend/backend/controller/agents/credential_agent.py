from typing import TypedDict, Optional
from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from astrapy import DataAPIClient
from backend.utils.embeddings import get_text_embedding
from backend.utils.file_reader import read_file_safely
from backend.config import main as config


# Define extracted fields
class CredentialFields(TypedDict, total=False):
    license_number: Optional[str]
    issue_date: Optional[str]
    expiry_date: Optional[str]
    institution: Optional[str]
    certifying_body: Optional[str]


class ExtractionState(TypedDict):
    file_path: str
    file_content: str
    extracted: CredentialFields


# Step 1: Read file content
def read_document(state: ExtractionState) -> ExtractionState:
    file_path = state["file_path"]

    try:
        content = read_file_safely(file_path)
    except Exception as e:
        raise ValueError(f"Failed to read file: {file_path}. Reason: {e}")

    new_state = dict(state)
    new_state["file_content"] = content
    return new_state


# Step 2: Extract credentials with Gemini
def extract_credentials(state: ExtractionState) -> ExtractionState:
    content = state["file_content"]

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest", google_api_key=config.GEMINI_API_KEY
    )

    prompt = f"""
Extract the following credential information from the medical document below:
- Name of the medical professional
- License number
- Issue date
- Expiry date (if available)
- Institution name
- Certifying body (e.g., MCI, NMC, GMC)

Respond in the following JSON format:

{{
  "name": "...",
  "license_number": "...",
  "issue_date": "...",
  "expiry_date": "...",
  "institution": "...",
  "certifying_body": "..."
}}

Provide the response only in JSON format without any additional text or no formatting needed.
Do not enclose the JSON in quotes or any other characters.
Strictly follow the JSON format.

Document:
\"\"\"
{content}
\"\"\"
    """

    response = llm.invoke(prompt)

    try:
        extracted = eval(response.content.strip())
    except Exception as e:
        raise ValueError(f"Invalid JSON from LLM: {response.content}") from e

    return {
        "file_path": state["file_path"],
        "file_content": content,
        "extracted": extracted,
    }


# Step 3: Format output
def format_output(state: ExtractionState) -> dict:
    return {"extracted_credentials": state["extracted"]}


# Build the LangGraph
def build_credential_extraction_agent():
    graph = StateGraph(ExtractionState)
    graph.add_node("ReadFile", read_document)
    graph.add_node("Extract", extract_credentials)
    graph.add_node("Format", format_output)

    graph.set_entry_point("ReadFile")
    graph.add_edge("ReadFile", "Extract")
    graph.add_edge("Extract", "Format")
    graph.set_finish_point("Format")

    return graph.compile()


# Async callable
async def extract_credentials_from_file(file_path: str) -> dict:
    graph = build_credential_extraction_agent()
    return await graph.ainvoke({"file_path": file_path})
