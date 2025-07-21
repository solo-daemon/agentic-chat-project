from fastapi import APIRouter, Depends, HTTPException, Header, Query
from starlette.status import HTTP_401_UNAUTHORIZED
import os
from typing import Optional
from dotenv import load_dotenv

# Ensure environment variables are loaded
load_dotenv()

router = APIRouter(prefix="/ask")

# Load the API key from the environment
EXPECTED_API_KEY = os.getenv("AGENT_API_KEY")

# Dependency to validate API key
async def verify_api_key(api_key: Optional[str] = Header(None)):
    if api_key != EXPECTED_API_KEY:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )

# Import your agent function
from agent.main import process_query  # Replace with actual import

@router.get("/")
async def ask_llm(
    query: str = Query(..., min_length=1, description="Query string for the agent"),
    _: None = Depends(verify_api_key),
):
    """Route that sends a query to the LLM agent after API key validation."""
    result = await process_query(query)
    return {"answer": result}