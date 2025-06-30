from astrapy import DataAPIClient
import os
from pathlib import Path
import json
from beanie import PydanticObjectId
from langgraph.graph import StateGraph, END, START
from langchain_core.runnables import RunnableLambda
from typing import TypedDict

from backend.config import main as config
from backend.utils.embeddings import get_text_embedding
from backend.utils.generate_random_string import generate_random_string
from backend.models.ReportHistory import ReportHistory

from backend.controller.agents.classifier_agent import classify_file as classifier_agent
from backend.controller.agents.credential_agent import (
    extract_credentials_from_file as extractor_agent,
)
from backend.controller.agents.verification_agent import (
    verify_extracted_credential as verifier_agent,
)
from backend.controller.agents.crosscheck_agent import (
    cross_check_all as crosscheck_agent,
)
from backend.controller.agents.credibility_agent import (
    evaluate_credibility as credibility_agent,
)

file_paths = [
    os.path.join(
        os.path.dirname(__file__), "..", "mock", "board_certificate_data.json"
    ),
    os.path.join(
        os.path.dirname(__file__), "..", "mock", "degree_certificate_data.json"
    ),
    os.path.join(os.path.dirname(__file__), "..", "mock", "medical_licence_data.json"),
    os.path.join(
        os.path.dirname(__file__), "..", "mock", "training_certificate_data.json"
    ),
]


async def create_vector_store() -> None:
    client = DataAPIClient(config.ASTRA_DB_SECRET_KEY)

    db = client.get_database_by_api_endpoint(
        config.ASTRA_DB_ENDPOINT,
        keyspace=config.ASTRA_DB_KEYSPACE,
    )

    collection = db.get_collection("embeddings")

    for file_path in file_paths:
        if not Path(file_path).exists():
            print(f"File not found: {file_path}")
            continue

        with open(file_path, "r", encoding="utf-8") as f:
            records = json.load(f)

        for record in records:
            text = json.dumps(record, ensure_ascii=False)
            doc_id = (
                record.get("certificate_id")
                or record.get("registration_number")
                or record.get("id")
                or record.get("license_number")
            )

            if not doc_id:
                # Use a fallback ID if needed
                doc_id = f"{hash(text)}"

            # Create embedding vector
            embedding = get_text_embedding(text)

            astra_doc = {
                "id": doc_id,
                "text": text,
                "$vector": embedding,
            }

            # Insert or update (upsert=True ensures no duplicates)
            collection.update_one({"id": doc_id}, {"$set": astra_doc}, upsert=True)


async def run_agent(file_paths: dict[str, str], curr_user) -> dict:

    # await create_vector_store() # Commenting out to avoid re-creating the vector store every time because its stored on astra db

    state_result = await orchestrator(file_paths=file_paths)
    result = state_result["formatted_response"]

    historical_entry = ReportHistory(
        user_id=curr_user.user_id,
        report_id=generate_random_string(7),
        credential_type=result["classifier_result"],
        credential_path=file_paths["credential_path"],
        validator_type="resume",
        validator_path=file_paths["resume_path"],
        result=result,
        status="completed",
    )

    await historical_entry.save()

    return result


class OrchestratorState(TypedDict):
    file_paths: dict[str, str]
    classifier_result: dict
    credential_result: dict
    verifier_result: dict
    crosscheck_result: dict
    credebility_result: dict
    formatted_response: dict


def response_formatter(state: OrchestratorState) -> dict:
    return {
        "formatted_response": {
            "classifier_result": state["classifier_result"]["document_type"],
            "credebility_result": (
                (
                    {
                        "credibility_score": 0,
                        "summary": "The uploaded credential is not a valid credential",
                        "flag": "red",
                        "discrepancies": [],
                    }
                )
                if state["classifier_result"]["document_type"]
                == "not_a_valid_credential"
                else state["credebility_result"]
            ),
        }
    }


def route_classification(state: dict) -> str:
    doc_type = state.get("classifier_result", {}).get("type")
    return "FORMATTER" if doc_type == "not_a_valid_credential" else "EXTRACTOR"


def orchestrator_agent():
    graph = StateGraph(OrchestratorState)
    graph.add_node("CLASSIFIER", classifier_agent)
    graph.add_node("ROUTE", route_classification)
    graph.add_node("EXTRACTOR", extractor_agent)
    graph.add_node("VERIFIER", verifier_agent)
    graph.add_node("CROSSCHECK", crosscheck_agent)
    graph.add_node("EVALUATOR", credibility_agent)
    graph.add_node("FORMATTER", response_formatter)

    graph.set_entry_point("CLASSIFIER")
    graph.add_edge(START, "CLASSIFIER")

    graph.add_conditional_edges("CLASSIFIER", route_classification)

    graph.add_edge("EXTRACTOR", "VERIFIER")
    graph.add_edge("VERIFIER", "CROSSCHECK")
    graph.add_edge("CROSSCHECK", "EVALUATOR")
    graph.add_edge("EVALUATOR", "FORMATTER")
    graph.add_edge("FORMATTER", END)

    graph.set_finish_point("FORMATTER")

    return graph.compile()


async def orchestrator(file_paths: dict[str, str]) -> dict:
    graph = orchestrator_agent()
    return await graph.ainvoke({"file_paths": file_paths})
