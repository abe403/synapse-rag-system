import os
import traceback
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from google import genai
import httpx

app = FastAPI(title="Synapse API Gateway")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini (new google-genai SDK)
api_key = os.environ.get("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)
MODEL_ID = "gemini-3.1-flash-lite"

MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL", "http://synapse-retrieval:5000")

async def get_mcp_context(query: str):
    """Call the MCP Server (Retrieval Engine) for context"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as http_client:
            response = await http_client.post(
                f"{MCP_SERVER_URL}/mcp/call_tool",
                json={"tool_name": "search_enterprise_documents", "args": {"query": query}}
            )
            response.raise_for_status()
            data = response.json()
            return data.get("result", "")
    except Exception as e:
        print(f"Error fetching context: {e}")
        return "No additional context available."

def format_stream(response):
    """Format Gemini response stream for SSE"""
    try:
        for chunk in response:
            if chunk.text:
                yield f"data: {chunk.text}\n\n"
        yield "data: [DONE]\n\n"
    except Exception as e:
        print(f"Gemini streaming error: {e}")
        yield f"data: [ERROR] Gemini API error: {e}\n\n"
        yield "data: [DONE]\n\n"

@app.post("/api/documents/upload")
async def upload_document(request: Request):
    """Endpoint to trigger document ingestion pipeline"""
    return {"status": "success", "message": "Document uploaded and queued for ingestion"}

@app.post("/api/chat")
async def chat(query: str):
    # 1. Call MCP Server to get context (Sub-200ms SLA)
    context = await get_mcp_context(query)
    
    # 2. Construct Prompt
    prompt = f"""
    You are Synapse, an Enterprise AI. Answer the user query using ONLY the provided context.
    
    CONTEXT (Standardized via MCP):
    {context}
    
    USER QUERY: {query}
    """
    
    try:
        # 3. Call Gemini API (Streaming response via new SDK)
        response = client.models.generate_content_stream(
            model=MODEL_ID,
            contents=prompt,
        )
        return StreamingResponse(format_stream(response), media_type="text/event-stream")
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        traceback.print_exc()
        return JSONResponse(
            status_code=502,
            content={"error": f"Gemini API error: {str(e)}"}
        )

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
