from langgraph.graph import StateGraph
from astrapy import DataAPIClient
from backend.config import main as config
from backend.utils.embeddings import get_text_embedding
from langchain_google_genai import ChatGoogleGenerativeAI
import json


def embed_and_retrieve_credential(state: dict) -> dict:
    credential_text = json.dumps(state["extracted"])

    embedding = get_text_embedding(credential_text)

    client = DataAPIClient(config.ASTRA_DB_SECRET_KEY)
    db = client.get_database_by_api_endpoint(
        config.ASTRA_DB_ENDPOINT, keyspace=config.ASTRA_DB_KEYSPACE
    )
    collection = db.get_collection("embeddings")

    results = collection.find({},sort={"$vector": embedding}, limit=1)

    retrieved_context = "\n---\n".join(r["text"] for r in results if "text" in r)

    return {**state, "retrieved_context": retrieved_context}


def validate_credential_with_llm(state: dict) -> dict:
    credential_text = state["extracted"]
    context = state["retrieved_context"]

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest", google_api_key=config.GEMINI_API_KEY
    )

    prompt = f"""
You are verifying the validity of a medical credential based on vector search results.

Credential to verify:
\"\"\"
{credential_text}
\"\"\"

Reference matches from the database:
\"\"\"
{context}
\"\"\"

Rules for validation:
1. If the name in the credential to verify matches the name in the reference matches (ignore case sensitivity), it is valid.
2. If the license number in the credential to verify matches the license number in the reference matches (ignore case sensitivity), it is valid.
3. If the issue date in the credential to verify matches the issue date in the reference matches (ignore case sensitivity), it is valid.
4. The expiry date can be in multiple names, it can be "expiry_date", "valid_until", "valid_through", "valid_till", etc. If the expiry date in the credential to verify matches any of these names in the reference matches (ignore case sensitivity), it is valid.
5. The institution name can be in multiple names, it can be "institution", "certifying_body", "certification_body", "university", etc. If the institution name in the credential to verify matches any of these names in the reference matches (ignore case sensitivity), it is valid.

It its invalid, respond with the reason why it is invalid.

If the credential is valid, respond with:
{{
  "status": "valid",
}}
If the credential is invalid, respond with:
{{
  "status": "invalid",
}}

Provide the response only in JSON string format without any additional text or no formatting needed.
Do not enclose the JSON string in quotes or any other characters.
Strictly follow the JSON string format.
"""

    try:
        response = llm.invoke(prompt)
        result = json.loads(response.content.strip())
        status = result["status"]
    except Exception as e:
        
        status = "invalid"

    return {"licence_record": credential_text, "status": status, "retrieved_context": context, "result": response.content}


def build_credential_verification_agent():
    graph = StateGraph(dict)

    graph.add_node("EmbedAndRetrieve", embed_and_retrieve_credential)
    graph.add_node("ValidateWithLLM", validate_credential_with_llm)

    graph.set_entry_point("EmbedAndRetrieve")
    graph.add_edge("EmbedAndRetrieve", "ValidateWithLLM")
    graph.set_finish_point("ValidateWithLLM")

    return graph.compile()


async def verify_extracted_credential(prev_state: dict) -> dict:
    
    graph = build_credential_verification_agent()
    result = await graph.ainvoke({"extracted": prev_state['credential_result']['extracted']})
    return {"verifier_result": result}
