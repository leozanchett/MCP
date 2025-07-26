from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import uvicorn
from typing import Dict, Any

app = FastAPI(title="MCP Math Server HTTP API", version="1.0.0")

# Modelos Pydantic para requisições
class MathOperation(BaseModel):
    a: int
    b: int

class GenericQuery(BaseModel):
    query: str

# Parâmetros do servidor MCP
server_params = StdioServerParameters(
    command="python",
    args=["math_server.py"]
)

async def call_mcp_tool(tool_name: str, arguments: Dict[str, Any]):
    """Função auxiliar para chamar ferramentas do MCP server"""
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                
                # Lista as ferramentas disponíveis
                tools = await session.list_tools()
                
                # Verifica se a ferramenta existe
                tool_exists = any(tool.name == tool_name for tool in tools.tools)
                if not tool_exists:
                    raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
                
                # Chama a ferramenta
                result = await session.call_tool(tool_name, arguments)
                return result.content[0].text if result.content else "No result"
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    """Endpoint raiz com informações da API"""
    return {
        "message": "MCP Math Server HTTP API",
        "version": "1.0.0",
        "endpoints": {
            "/add": "POST - Soma dois números",
            "/subtract": "POST - Subtrai dois números",
            "/tools": "GET - Lista todas as ferramentas disponíveis"
        }
    }

@app.get("/tools")
async def list_tools():
    """Lista todas as ferramentas disponíveis no MCP server"""
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                return {
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        }
                        for tool in tools.tools
                    ]
                }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/add")
async def add_numbers(operation: MathOperation):
    """Endpoint para somar dois números"""
    result = await call_mcp_tool("add", {"a": operation.a, "b": operation.b})
    return {
        "operation": "addition",
        "a": operation.a,
        "b": operation.b,
        "result": int(result)
    }

@app.post("/subtract")
async def subtract_numbers(operation: MathOperation):
    """Endpoint para subtrair dois números"""
    result = await call_mcp_tool("subtract", {"a": operation.a, "b": operation.b})
    return {
        "operation": "subtraction",
        "a": operation.a,
        "b": operation.b,
        "result": int(result)
    }

@app.post("/calculate")
async def generic_calculation(query: GenericQuery):
    """Endpoint genérico para cálculos usando linguagem natural"""
    # Este endpoint poderia integrar com um LLM para interpretar a query
    # Por enquanto, retorna uma mensagem informativa
    return {
        "message": "Endpoint para cálculos com linguagem natural",
        "query": query.query,
        "suggestion": "Use os endpoints /add ou /subtract para operações específicas",
        "note": "Atualmente, apenas operações aritméticas são suportadas"
    }

if __name__ == "__main__":
    print("Iniciando servidor HTTP na porta 8000...")
    print("Documentação da API disponível em: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)