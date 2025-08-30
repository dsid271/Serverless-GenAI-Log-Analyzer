import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI 
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate

load_dotenv()
gemini_api_key = os.getenv("GOOGLE_API_KEY")

if not gemini_api_key:
    raise ValueError("API key not set.")

app = FastAPI(title="Serverless GenAI Log Analyzer")
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=gemini_api_key)

class LogEntry(BaseModel):
    # Using a flexible schema to handle various log formats
    # We can accept a dictionary where keys are strings and values can be any type
    log_data: Dict[str, Any]

class LogAnalysisRequest(BaseModel):
    logs: List[LogEntry]

# Create a simple, powerful prompt for network log analysis
prompt_template = PromptTemplate.from_template(
    "You are an expert network analyst. Analyze the following network logs to "
    "identify any potential issues, anomalies, or security threats. "
    "Summarize your findings, and provide key insights. "
    "Here are the network logs:\n\n{logs_json}"
)

@app.post("/analyze_log", tags = ["Log Analysis"])
async def analyze_log(request: LogAnalysisRequest):
    """
    Accepts a list of network logs and returns an AI-generated analysis.
    """
    if not request.logs:
        raise HTTPException(status_code=400, detail="No log entries provided.")
    
    try:
        # Convert the list of Pydantic models to a JSON string
        logs_json = [log.log_data for log in request.log]
        formatted_prompt = prompt_template.format()

        # Generate the response using the Gemini model
        response = llm(formatted_prompt)

        return {
            "status": "success",
            "analysis": response.content,
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))