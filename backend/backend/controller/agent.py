from astrapy import DataAPIClient
import os
from pathlib import Path
import json
from backend.config import main as config
from backend.utils.embeddings import get_text_embedding

from backend.controller.agents.classifier_agent import classify_file
from backend.controller.agents.credential_agent import extract_credentials_from_file
from backend.controller.agents.verification_agent import verify_extracted_credential
from backend.controller.agents.crosscheck_agent import cross_check_all
from backend.controller.agents.credibility_agent import evaluate_credibility

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


async def run_agent(file_paths: dict[str, str]) -> dict:

    # await create_vector_store() # Commenting out to avoid re-creating the vector store every time because its stored on astra db

    classifier_result = (await classify_file(file_paths["credential_path"]))['document_type']
    credential_result = (await extract_credentials_from_file(file_paths["credential_path"]))['extracted']
    verifier_result = (await verify_extracted_credential(json.dumps(credential_result)))['status']
    crosscheck_result = await cross_check_all(credential_result, verifier_result, file_paths["resume_path"])
    credebility_result = await evaluate_credibility(crosscheck_result, verifier_result)
    
    return {
        "classifier_result": classifier_result,
        "credebility_result": credebility_result,
    }
