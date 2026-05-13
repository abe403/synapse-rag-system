from mcp.server.fastmcp import FastMCP
from fastapi import FastAPI, Request
from pydantic import BaseModel
from embedder import embedder

# Initialize FastMCP Server
mcp = FastMCP("Synapse-Retrieval-Engine")

def format_as_mcp_context(results):
    """Format results into a standardized context string."""
    context = ""
    for i, res in enumerate(results):
        context += f"[Document {i+1}]: {res}\n\n"
    return context.strip()

@mcp.tool()
def search_enterprise_documents(query: str, top_k: int = 3) -> str:
    """Search the FAISS index for relevant enterprise context."""
    results = embedder.search(query, top_k)
    return format_as_mcp_context(results)

# Exposing a simple REST wrapper for the tool for simplicity in docker-compose.
app = FastAPI(title="Synapse Retrieval Engine MCP Bridge")

class ToolRequest(BaseModel):
    tool_name: str
    args: dict

@app.post("/mcp/call_tool")
async def call_tool(req: ToolRequest):
    if req.tool_name == "search_enterprise_documents":
        query = req.args.get("query", "")
        top_k = req.args.get("top_k", 3)
        result = search_enterprise_documents(query, top_k)
        return {"result": result}
    return {"result": "Tool not found"}

@app.get("/health")
def health():
    return {"status": "ok", "indexed_documents": embedder.index.ntotal}
