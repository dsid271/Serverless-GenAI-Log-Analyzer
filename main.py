import os
from typing import List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import uvicorn

load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY environment variable not set.")

app = FastAPI(title="Serverless GenAI Log Analyzer")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)

class LogEntry(BaseModel):
    log_data: Dict[str, Any]

class LogAnalysisRequest(BaseModel):
    logs: List[LogEntry]

prompt_template = PromptTemplate.from_template(
    "You are an expert network analyst. Analyze the following network logs to "
    "identify any potential issues, anomalies, or security threats. "
    "Summarize your findings, and provide key insights. "
    "Here are the network logs:\n\n{logs_json}"
)

@app.post("/analyze-log", tags=["Log Analysis"])
async def analyze_log(request: LogAnalysisRequest):
    """
    Accepts a list of network logs and returns an AI-generated analysis.
    """
    if not request.logs:
        raise HTTPException(status_code=400, detail="No log entries provided.")

    try:
        logs_json = [log.log_data for log in request.logs]
        formatted_prompt = prompt_template.format(logs_json=logs_json)
        response = llm.invoke(formatted_prompt)

        return {
            "status": "success",
            "analysis": response.content,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
