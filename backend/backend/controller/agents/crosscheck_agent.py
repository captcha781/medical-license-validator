from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import main as config
from backend.utils.file_reader import read_file_safely
import json
from langgraph.graph import StateGraph


def cross_check_with_gemini(state: dict) -> dict:
    extracted = state["extracted"]
    verification = state["verification"]
    resume_path = state["resume_path"]

    resume_text = read_file_safely(resume_path)

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest", google_api_key=config.GEMINI_API_KEY
    )

    prompt = f"""
You are an expert medical document auditor.

Compare the following three sources and report any inconsistencies:

1. Credential extraction:
{extracted}

2. Credential verification:
{json.dumps(verification, indent=2)}

3. Resume content:
\"\"\"
{resume_text}
\"\"\"

Check consistency across:
- Name
- License number
- Institution / University
- Certifying Body
- Issuance Date
- Expiry Date

Support minor name variations (e.g., “Harvard” vs “Harvard Medical School”), date formats, and fuzzy matching.
Detect inconsistencies or mismatches (e.g., Resume claims 2020 degree, but issue date is 2022).

Return a JSON object with the following structure, only use json plain text without any additional text or formatting:
{{
  "consistency_report": {{
    "name_match": true/false,
    "license_number_match": true/false,
    "institution_match": true/false,
    "certifying_body_match": true/false,
    "issue_date_match": true/false,
    "expiry_date_match": true/false
  }},
  "discrepancies": [
    "...",
    "..."
  ]
}}

Provide the response only in JSON string format without any additional text or no formatting needed.
Do not enclose the response in any json identifier or triple backticks.
Do not enclose the JSON string in quotes or any other characters.
Strictly follow the JSON string format.
"""

    try:
        response = llm.invoke(prompt)
        print(response.content)
        result = json.loads(response.content.strip())
        return {"result": result}
    except Exception as e:
        return {"consistency_report": {}, "discrepancies": [f"LLM error: {str(e)}"]}


def build_cross_check_agent():
    graph = StateGraph(dict)
    graph.add_node("CrossCheck", cross_check_with_gemini)
    graph.set_entry_point("CrossCheck")
    graph.set_finish_point("CrossCheck")
    return graph.compile()


async def cross_check_all(prev_state: dict) -> dict:
    graph = build_cross_check_agent()
    result = await graph.ainvoke(
        {
            "extracted": prev_state['credential_result']['extracted'],
            "verification": prev_state['verifier_result']['status'],
            "resume_path": prev_state["file_paths"]["resume_path"],
        }
    )
    
    return {"crosscheck_result": result}
