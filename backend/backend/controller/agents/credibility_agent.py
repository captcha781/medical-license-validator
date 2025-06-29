from langgraph.graph import StateGraph
from langchain_google_genai import ChatGoogleGenerativeAI
from backend.config import main as config
import json

def calculate_credibility_score(state: dict) -> dict:
    crosscheck = state["crosscheck"]
    verification = state["verification"]

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash-latest",
        google_api_key=config.GEMINI_API_KEY
    )

    prompt = f"""
You are a medical credential assessment agent.

Your task is to analyze the consistency report and verification result of a doctor's credentials and provide a credibility score between 0 and 10.

Inputs:
1. Consistency report:
{json.dumps(crosscheck, indent=2)}

2. Verification result:
{json.dumps(verification, indent=2)}

Scoring guidelines:
- If verification status is 'valid', start with a base score of 6. If 'invalid', start with 20.
- Add valid by points yourself based on consistency_report (e.g., name_match, license_number_match, etc).
- Cap score between 0 and 100.
- Listout the discrepancies in the verification result that led to the score.
- Provide a summary of the analysi including discrepancies.
- Based on the analysis, provide a risk flag indicating if the credentials are credible or not., use red/yellow/green

Respond with this format ONLY:
{{
  "credibility_score": score out of 100,
  "summary": "summary of the analysis",
  "flag": "red/yellow/green",
  "discrepancies": ["list", "of", "discrepancies"]
}}

Provide the response only in JSON string format without any additional text or no formatting needed.
Do not enclose the response in any json identifier or triple backticks.
Do not enclose the JSON string in quotes or any other characters.
Strictly follow the JSON string format.
"""

    try:
        response = llm.invoke(prompt)
        result = json.loads(response.content.strip())
        return result
    except Exception as e:
        return {
            "credibility_score": 0,
            "summary": f"Failed to compute credibility score due to error: {str(e)}"
        }


def build_credibility_score_agent():
    graph = StateGraph(dict)
    graph.add_node("EvaluateCredibility", calculate_credibility_score)
    graph.set_entry_point("EvaluateCredibility")
    graph.set_finish_point("EvaluateCredibility")
    return graph.compile()


async def evaluate_credibility(prev_state: dict) -> dict:
    graph = build_credibility_score_agent()
    result = await graph.ainvoke({
        "crosscheck": prev_state['crosscheck_result'],
        "verification": prev_state['verifier_result']['status']
    })
    
    return {"credebility_result": result}
